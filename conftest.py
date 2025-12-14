"""
Конфигурация pytest и общие фикстуры
"""
import pytest
import allure
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, browser_name):
    """Настройка контекста браузера для разных браузеров"""
    base_args = {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "locale": "ru-RU",
        "timezone_id": "Europe/Moscow",
    }
    
    # Специфичные настройки для разных браузеров
    if browser_name == "firefox":
        base_args.update({
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        })
    elif browser_name == "webkit":
        base_args.update({
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        })
    
    return base_args


@pytest.fixture(scope="function")
def context(browser: Browser, browser_name):
    """Создание нового контекста для каждого теста"""
    context_args = {
        "viewport": {"width": 1920, "height": 1080},
        "locale": "ru-RU",
        "timezone_id": "Europe/Moscow",
    }
    
    # Добавляем специфичные настройки для браузеров
    if browser_name == "firefox":
        context_args["user_agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    elif browser_name == "webkit":
        context_args["user_agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    
    context = browser.new_context(**context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, request, browser_name):
    """Создание новой страницы для каждого теста"""
    page = context.new_page()
    
    # Добавляем информацию о браузере в Allure
    allure.attach(
        browser_name.upper(),
        name="Браузер",
        attachment_type=allure.attachment_type.TEXT
    )
    
    yield page
    
    # Создание скриншота при ошибке теста
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        try:
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name=f"screenshot_{browser_name}_{request.node.name}",
                attachment_type=allure.attachment_type.PNG
            )
        except Exception:
            pass
    
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для получения результата теста"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
