"""
复旦EE招生素材生成器 - FastAPI 主服务
"""

import re
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
import time
import asyncio
import threading
import tempfile
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from claude_client import ClaudeClient
from openai_client import GPTClient
from settings import get_settings, validate_ai_config


settings = get_settings()

# 启动时验证 AI API 配置
try:
    validate_ai_config()
except ValueError as e:
    logger.warning(f"配置验证警告: {e}")
    logger.warning("应用将启动，但部分功能可能不可用")


GENERATE_MAX_OUTPUT_TOKENS_DEFAULT = GeminiClient._load_positive_int_env(
    "GEMINI_GENERATE_MAX_OUTPUT_TOKENS_DEFAULT", 10000
)
EDIT_MAX_OUTPUT_TOKENS = GeminiClient._load_positive_int_env(
    "GEMINI_EDIT_MAX_OUTPUT_TOKENS", 15000
)

MATERIAL_MAX_OUTPUT_TOKENS = {
    "recruit-poster": 12000,
    "event-poster": 12000,
    "class-notice": 10000,
    "recruit-page": 15000,
    "student-profile": 12000,
    "landing-page": 15000,
    "student-handbook": 16000,
    "long-image": 16000,
    "trifold-brochure": 16000,
}


# 初始化 FastAPI
app = FastAPI(title=settings.app_name, version=settings.app_version)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
BASE_DIR = Path(__file__).parent
VISUAL_ASSETS_DIR = settings.visual_assets_dir
HISTORY_DIR = settings.history_dir

# 确保历史目录存在
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

gemini_client = GeminiClient()
claude_client = ClaudeClient()
gpt_client = GPTClient()
prompt_builder = PromptBuilder(base_dir=BASE_DIR)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# 挂载视觉资产目录
if VISUAL_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(VISUAL_ASSETS_DIR)), name="assets")


# ==================== 数据模型 ====================

class GenerateRequest(BaseModel):
    """生成素材请求"""
    course_id: str
    material_type: str
    user_requirements: str = ""
    custom_prompt: Optional[str] = None
    # Phase 2: 生成前细分控制
    visual_style: Optional[str] = None
    narrative_style: Optional[str] = None
    layout_structure: Optional[str] = None
    visual_elements: Optional[str] = None
    content_presentation: Optional[str] = None
    # Phase 2: 局部内容开关
    include_faculty: bool = True
    include_schedule: bool = True
    include_tuition: bool = True
    include_student_profile: bool = True
    include_curriculum: bool = True
    include_certification: bool = True
    # Phase 2: 视觉资产
    logo_url: Optional[str] = None
    background_url: Optional[str] = None


class ExportRequest(BaseModel):
    """导出请求"""
    html: str
    format: str  # "pdf" or "png" or "html"
    filename: str
    export_width: int = 750  # PNG 导出宽度，跟随素材类型


class EditRequest(BaseModel):
    """对话式微调请求"""
    current_html: str
    edit_instruction: str
    course_id: str
    material_type: str
    use_claude: bool = False  # 是否使用 Claude API
    use_gpt: bool = False     # 是否使用 GPT API


class SaveHistoryRequest(BaseModel):
    """手动保存历史记录请求"""
    course_id: Optional[str] = None
    material_type: Optional[str] = None
    html: str
    prompt: Optional[str] = None
    model_used: Optional[str] = None
    user_requirements: Optional[str] = ""
    request_params: Optional[dict[str, Any]] = None


# ==================== API 接口 ====================

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """统一处理未捕获的异常"""
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )

@app.get("/api/claude/status")
async def claude_status():
    """检查 Claude API 是否可用"""
    return JSONResponse(content={
        "available": claude_client.is_available()
    })

@app.get("/")
async def root():
    """根路径，返回前端页面"""
    return FileResponse(str(BASE_DIR / "static" / "index.html"))


@app.get("/api/courses")
async def get_courses():
    """获取所有课程列表"""
    try:
        courses = prompt_builder.get_courses()
        return JSONResponse(content=courses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/material-types")
async def get_material_types():
    """获取所有素材类型列表"""
    try:
        material_types = prompt_builder.get_material_types()
        return JSONResponse(content=material_types)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visual-assets")
async def get_visual_assets():
    """获取可用的视觉资产列表"""
    try:
        assets = {
            "logos": []
        }

        if VISUAL_ASSETS_DIR.exists():
            # 扫描 Logo 文件（从 02_EE项目标识与Logo 目录）
            logo_dir = VISUAL_ASSETS_DIR / "02_EE项目标识与Logo"
            if logo_dir.exists():
                for file in logo_dir.glob("*.png"):
                    assets["logos"].append({
                        "name": file.name,
                        "url": f"/assets/02_EE项目标识与Logo/{file.name}"
                    })
                for file in logo_dir.glob("*.jpg"):
                    assets["logos"].append({
                        "name": file.name,
                        "url": f"/assets/02_EE项目标识与Logo/{file.name}"
                    })

        return JSONResponse(content=assets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/stream")
async def generate_material_stream(request: GenerateRequest):
    """流式生成素材，通过 SSE 实时推送进度"""
    try:
        prompt = _build_prompt_from_request(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    max_output_tokens = MATERIAL_MAX_OUTPUT_TOKENS.get(
        request.material_type, GENERATE_MAX_OUTPUT_TOKENS_DEFAULT
    )
    start_time = time.time()

    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()
        full_text = ""
        model_used: list = [None]

        def stream_thread():
            try:
                for chunk_text, model_name in gemini_client.stream_generate(
                    prompt, max_output_tokens=max_output_tokens
                ):
                    model_used[0] = model_name
                    loop.call_soon_threadsafe(queue.put_nowait, ("chunk", chunk_text))
                loop.call_soon_threadsafe(queue.put_nowait, ("done", None))
            except Exception as exc:
                # 流式失败时降级到 Claude
                if claude_client.is_available():
                    loop.call_soon_threadsafe(queue.put_nowait, ("fallback", str(exc)))
                else:
                    loop.call_soon_threadsafe(queue.put_nowait, ("error", str(exc)))

        threading.Thread(target=stream_thread, daemon=True).start()

        while True:
            try:
                event_type, data = await asyncio.wait_for(queue.get(), timeout=120.0)
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'error', 'message': '生成超时'})}\n\n"
                return

            if event_type == "chunk":
                full_text += data
                yield f"data: {json.dumps({'type': 'chunk', 'text': data, 'total_len': len(full_text)})}\n\n"

            elif event_type == "done":
                html = extract_html_from_response(full_text)
                elapsed = round(time.time() - start_time, 1)
                logger.info(f"✨ 流式生成完成，耗时 {elapsed}s，HTML {len(html)} 字符")
                yield f"data: {json.dumps({'type': 'done', 'html': html, 'model_used': model_used[0], 'prompt_used': prompt})}\n\n"
                return

            elif event_type == "fallback":
                logger.warning(f"流式失败，降级到 Claude：{data[:120]}")
                try:
                    response_text, model = claude_client.optimize(prompt)
                    html = extract_html_from_response(response_text)
                    yield f"data: {json.dumps({'type': 'done', 'html': html, 'model_used': model, 'prompt_used': prompt})}\n\n"
                except Exception as e2:
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e2)})}\n\n"
                return

            elif event_type == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data})}\n\n"
                return

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/api/generate")
async def generate_material(request: GenerateRequest):
    """生成素材"""
    try:
        start_time = time.time()

        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 开始生成素材 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*70}")
        logger.info(f"📋 课程: {request.course_id}")
        logger.info(f"📄 素材类型: {request.material_type}")
        logger.info(f"📝 用户要求: {request.user_requirements[:100] if request.user_requirements else '无'}")
        logger.info(f"🎭 视觉风格: {request.visual_style or '默认'}")
        logger.info(f"🎨 叙事风格: {request.narrative_style or '默认'}")
        logger.info(f"📐 排版结构: {request.layout_structure or '默认'}")
        logger.info(f"🖼️  视觉元素: {request.visual_elements or '默认'}")
        logger.info(f"📊 内容呈现: {request.content_presentation or '默认'}")
        logger.info(f"{'='*70}\n")

        # 步骤1: 构建提示词
        step1_start = time.time()
        logger.info(f"⚙️  [步骤 1/3] 构建提示词...")
        prompt = _build_prompt_from_request(request)
        logger.info(f"   - 提示词长度: {len(prompt)} 字符")
        logger.info(f"   - 耗时: {time.time() - step1_start:.2f}秒\n")

        # 步骤2: 调用 Gemini 生成（失败时自动降级到 Claude）
        step2_start = time.time()
        logger.info(f"🤖 [步骤 2/3] 调用 Gemini API 生成内容...")
        max_output_tokens = MATERIAL_MAX_OUTPUT_TOKENS.get(
            request.material_type,
            GENERATE_MAX_OUTPUT_TOKENS_DEFAULT,
        )
        logger.info(f"   - max_output_tokens: {max_output_tokens}")
        try:
            response_text, model_used = gemini_client.generate(
                prompt,
                max_output_tokens=max_output_tokens,
            )
        except Exception as gemini_error:
            logger.error(f" Gemini 失败: {str(gemini_error)[:200]}")
            if claude_client.is_available():
                logger.info(f"   ↪ 自动降级到 Claude 继续生成...")
                response_text, model_used = claude_client.optimize(prompt)
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"Gemini 暂时不可用，且 Claude 未配置。原始错误: {str(gemini_error)}"
                ) from gemini_error
        step2_time = time.time() - step2_start
        logger.info(f"   ✅ AI API 调用成功")
        logger.info(f"   - 使用模型: {model_used}")
        logger.info(f"   - 响应长度: {len(response_text)} 字符")
        logger.info(f"   - 耗时: {step2_time:.2f}秒\n")

        # 步骤3: 提取 HTML 代码
        step3_start = time.time()
        logger.info(f"📝 [步骤 3/3] 提取 HTML 代码...")
        html = extract_html_from_response(response_text)
        logger.info(f"   ✅ HTML 提取成功")
        logger.info(f"   - HTML 长度: {len(html)} 字符")
        logger.info(f"   - 耗时: {time.time() - step3_start:.2f}秒\n")

        total_time = time.time() - start_time
        logger.info(f"{'='*70}")
        logger.info(f"✨ 素材生成完成！")
        logger.info(f"⏱️  总耗时: {total_time:.2f}秒")
        logger.info(f"{'='*70}\n")

        return JSONResponse(content={
            "html": html,
            "prompt_used": prompt,
            "model_used": model_used,
            "history_id": None
        })

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        if isinstance(e, ValueError):
            raise HTTPException(status_code=400, detail=str(e))
        logger.error(f"生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/edit")
async def edit_material(request: EditRequest):
    """对话式微调素材 - 支持 Gemini 和 Claude"""
    try:
        start_time = time.time()

        logger.info(f"\n{'='*70}")
        logger.info(f"✏️  开始对话式微调 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*70}")
        logger.info(f"📋 课程: {request.course_id}")
        logger.info(f"📄 素材类型: {request.material_type}")
        logger.info(f"💬 修改指令: {request.edit_instruction[:100]}...")
        model_display = 'Claude Sonnet 4.6' if request.use_claude else ('GPT' if request.use_gpt else 'Gemini')
        logger.info(f"🤖 使用模型: {model_display}")
        logger.info(f"📏 当前HTML长度: {len(request.current_html)} 字符")
        logger.info(f"{'='*70}\n")

        # 构建增量修改的提示词
        logger.info(f"⚙️  [步骤 1/3] 构建微调提示词...")
        edit_prompt = f"""你是一个HTML/CSS专家。用户有一个已经生成的营销素材HTML代码，现在需要根据用户的修改指令进行增量修改。

**重要要求**：
1. 不要推翻重来，只需要根据用户的修改指令对现有HTML进行局部调整
2. 保持原有的整体结构和风格
3. 只修改用户明确要求修改的部分
4. 确保修改后的HTML代码完整且可以直接渲染

**当前HTML代码**：
```html
{request.current_html}
```

**用户的修改指令**：
{request.edit_instruction}

**课程信息**：
- 课程ID: {request.course_id}
- 素材类型: {request.material_type}

请根据用户的修改指令，对上述HTML代码进行增量修改，并返回完整的修改后的HTML代码。
只返回HTML代码，不要有任何其他说明文字。代码必须用```html和```包裹。
"""
        logger.info(f"   ✅ 提示词构建完成")
        logger.info(f"   - 提示词长度: {len(edit_prompt)} 字符\n")

        # 步骤2: 调用 AI API
        step2_start = time.time()
        model_name = 'Claude' if request.use_claude else ('GPT' if request.use_gpt else 'Gemini')
        logger.info(f"🤖 [步骤 2/3] 调用 {model_name} API 进行微调...")

        # 根据选择调用不同的 API
        if request.use_claude:
            if not claude_client.is_available():
                logger.error(f" Claude API 未配置")
                raise HTTPException(
                    status_code=400,
                    detail="Claude API 未配置，请在 .env 文件中添加 ANTHROPIC_API_KEY 或 CLAUDE_API_KEY"
                )
            response_text, model_used = claude_client.optimize(edit_prompt)
        elif request.use_gpt:
            if not gpt_client.is_available():
                logger.error(f" GPT API 未配置")
                raise HTTPException(
                    status_code=400,
                    detail="GPT API 未配置，请在 cc-switch 中添加 codex provider"
                )
            response_text, model_used = gpt_client.optimize(edit_prompt, max_tokens=EDIT_MAX_OUTPUT_TOKENS)
        else:
            logger.info(f"   - max_output_tokens: {EDIT_MAX_OUTPUT_TOKENS}")
            response_text, model_used = gemini_client.generate(
                edit_prompt,
                max_output_tokens=EDIT_MAX_OUTPUT_TOKENS,
            )

        step2_time = time.time() - step2_start
        logger.info(f"   ✅ API 调用成功")
        logger.info(f"   - 使用模型: {model_used}")
        logger.info(f"   - 响应长度: {len(response_text)} 字符")
        logger.info(f"   - 耗时: {step2_time:.2f}秒\n")

        # 步骤3: 提取 HTML 代码
        step3_start = time.time()
        logger.info(f"📝 [步骤 3/3] 提取修改后的 HTML...")
        html = extract_html_from_response(response_text)
        logger.info(f"   ✅ HTML 提取成功")
        logger.info(f"   - HTML 长度: {len(html)} 字符")
        logger.info(f"   - 耗时: {time.time() - step3_start:.2f}秒\n")

        total_time = time.time() - start_time
        logger.info(f"{'='*70}")
        logger.info(f"✨ 对话式微调完成！")
        logger.info(f"⏱️  总耗时: {total_time:.2f}秒")
        logger.info(f"{'='*70}\n")

        return JSONResponse(content={
            "html": html,
            "prompt_used": edit_prompt,
            "model_used": model_used,
            "history_id": None
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"微调失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history():
    """获取历史记录列表"""
    try:
        history_list = get_history_list()
        return JSONResponse(content=history_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/history")
async def save_history_manually(request: SaveHistoryRequest):
    """手动保存历史记录"""
    try:
        if not (request.html or "").strip():
            raise HTTPException(status_code=400, detail="html 不能为空")

        history_id = save_history(
            course_id=(request.course_id or "CUSTOM"),
            material_type=(request.material_type or "custom"),
            html=request.html,
            prompt=request.prompt or "",
            model_used=request.model_used or "manual",
            user_requirements=request.user_requirements or "",
            request_params=request.request_params or {},
        )
        return JSONResponse(content={"success": True, "history_id": history_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{history_id}")
async def get_history_by_id(history_id: str):
    """获取历史记录详情"""
    try:
        history_detail = get_history_detail(history_id)
        if not history_detail:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        return JSONResponse(content=history_detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/history/{history_id}")
async def delete_history_by_id(history_id: str):
    """删除单条历史记录"""
    try:
        deleted = delete_history_item(history_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        return JSONResponse(content={"success": True, "id": history_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Playwright 浏览器池 ====================

_playwright_instance = None
_playwright_browser = None
_playwright_lock = asyncio.Lock()


async def _get_browser():
    """获取或创建共享的 Playwright 浏览器实例（懒加载，进程级复用）"""
    global _playwright_instance, _playwright_browser
    async with _playwright_lock:
        if _playwright_browser and _playwright_browser.is_connected():
            return _playwright_browser
        from playwright.async_api import async_playwright
        _playwright_instance = await async_playwright().start()
        _playwright_browser = await _playwright_instance.chromium.launch(headless=True)
        logger.info("Playwright 浏览器实例已创建（将复用）")
        return _playwright_browser


@app.on_event("shutdown")
async def _shutdown_playwright():
    """应用关闭时释放浏览器"""
    global _playwright_instance, _playwright_browser
    if _playwright_browser:
        await _playwright_browser.close()
    if _playwright_instance:
        await _playwright_instance.stop()
    logger.info("Playwright 浏览器已关闭")


@app.post("/api/export")
async def export_material(request: ExportRequest):
    """导出素材为 PDF、图片或 HTML - 直接下载到浏览器"""
    from starlette.background import BackgroundTask
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    def cleanup():
        shutil.rmtree(temp_dir, ignore_errors=True)

    try:
        # 保存 HTML
        html_path = temp_path / "output.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(request.html)

        if request.format == "html":
            return FileResponse(
                path=str(html_path),
                filename=f"{request.filename}.html",
                media_type="text/html",
                background=BackgroundTask(cleanup),
            )

        browser = await _get_browser()

        if request.format == "pdf":
            output_path = temp_path / f"{request.filename}.pdf"
            page = await browser.new_page()
            try:
                await page.goto(f'file://{html_path}')
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(1000)
                await page.pdf(
                    path=str(output_path),
                    format='A4',
                    print_background=True,
                    margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
                )
            finally:
                await page.close()

            return FileResponse(
                path=str(output_path),
                filename=f"{request.filename}.pdf",
                media_type="application/pdf",
                background=BackgroundTask(cleanup),
            )

        elif request.format == "png":
            output_path = temp_path / f"{request.filename}.png"
            render_width = request.export_width
            page = await browser.new_page(
                viewport={'width': render_width, 'height': 2000},
                device_scale_factor=2
            )
            try:
                await page.goto(f'file://{html_path}')
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(1000)

                page_height = await page.evaluate('document.documentElement.scrollHeight')
                await page.set_viewport_size({'width': render_width, 'height': page_height})
                await page.wait_for_timeout(500)

                await page.screenshot(
                    path=str(output_path),
                    full_page=True,
                    type='png'
                )
            finally:
                await page.close()

            return FileResponse(
                path=str(output_path),
                filename=f"{request.filename}.png",
                media_type="image/png",
                background=BackgroundTask(cleanup),
            )

        else:
            raise ValueError(f"不支持的导出格式: {request.format}")

    except Exception as e:
        cleanup()
        logger.error(f"导出失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 辅助函数 ====================

def _build_prompt_from_request(request: GenerateRequest) -> str:
    """从生成请求构建提示词（统一两个 generate 端点的参数传递）"""
    return prompt_builder.build_prompt(
        course_id=request.course_id,
        material_type=request.material_type,
        user_requirements=request.user_requirements,
        custom_prompt=request.custom_prompt,
        visual_style=request.visual_style,
        narrative_style=request.narrative_style,
        layout_structure=request.layout_structure,
        visual_elements=request.visual_elements,
        content_presentation=request.content_presentation,
        include_faculty=request.include_faculty,
        include_schedule=request.include_schedule,
        include_tuition=request.include_tuition,
        include_student_profile=request.include_student_profile,
        include_curriculum=request.include_curriculum,
        include_certification=request.include_certification,
        logo_url=request.logo_url,
        background_url=request.background_url,
    )


def save_history(course_id: str, material_type: str, html: str, prompt: str,
                 model_used: str, user_requirements: str, request_params: dict) -> str:
    """保存生成历史记录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_course_id = re.sub(r"[^A-Za-z0-9._-]+", "-", course_id or "CUSTOM").strip("-_.") or "CUSTOM"
    safe_material_type = re.sub(r"[^A-Za-z0-9._-]+", "-", material_type or "custom").strip("-_.") or "custom"
    history_id = f"{timestamp}_{safe_course_id}_{safe_material_type}"

    history_data = {
        "id": history_id,
        "timestamp": timestamp,
        "course_id": course_id,
        "material_type": material_type,
        "html": html,
        "prompt": prompt,
        "model_used": model_used,
        "user_requirements": user_requirements,
        "request_params": request_params
    }

    history_file = HISTORY_DIR / f"{history_id}.json"
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    return history_id


def get_history_list():
    """获取历史记录列表"""
    history_files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)
    history_list = []

    for file in history_files[:50]:  # 最多返回50条
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history_list.append({
                    "id": data.get("id"),
                    "timestamp": data.get("timestamp"),
                    "course_id": data.get("course_id"),
                    "material_type": data.get("material_type"),
                    "model_used": data.get("model_used"),
                    "user_requirements": data.get("user_requirements", "")[:100]  # 截取前100字符
                })
        except Exception as e:
            logger.warning(f"读取历史记录失败: {file.name}, {str(e)}")
            continue

    return history_list


def get_history_detail(history_id: str):
    """获取历史记录详情"""
    history_file = HISTORY_DIR / f"{history_id}.json"

    if not history_file.exists():
        return None

    with open(history_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def delete_history_item(history_id: str) -> bool:
    """删除历史记录文件"""
    if "/" in history_id or "\\" in history_id or ".." in history_id:
        return False

    history_file = HISTORY_DIR / f"{history_id}.json"
    if not history_file.exists():
        return False

    history_file.unlink()
    return True


def extract_html_from_response(response_text: str) -> str:
    """从 Gemini 响应中提取 HTML 代码"""
    # 尝试提取 ```html ... ``` 代码块
    pattern = r"```html\s*(.*?)\s*```"
    match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 没有闭合代码块时，从 <!DOCTYPE html> 或 <html> 开始提取
    if "<!DOCTYPE html>" in response_text or "<html" in response_text:
        start_idx = response_text.find("<!DOCTYPE html>")
        if start_idx == -1:
            start_idx = response_text.find("<html")

        end_idx = response_text.rfind("</html>")
        if end_idx != -1:
            return response_text[start_idx:end_idx + 7].strip()

        # 响应被截断（token 超限）：返回从 HTML 起始位置到末尾的内容
        return response_text[start_idx:].strip()

    # 兜底：返回原始响应
    return response_text.strip()


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
