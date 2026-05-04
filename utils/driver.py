"""WebDriver setup and management for FotMob scraper."""

import os
import shutil
from pathlib import Path

from requests.exceptions import ConnectionError as RequestsConnectionError
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def _resolve_edge_driver_path():
    """Find a locally available Edge WebDriver binary if one exists."""
    project_root = Path(__file__).resolve().parents[1]
    sibling_driver = project_root.parent / "edgedriver_win64" / "msedgedriver.exe"
    if sibling_driver.exists():
        return str(sibling_driver)

    for env_var in ("EDGE_DRIVER_PATH", "MSEDGEDRIVER_PATH"):
        configured_path = os.getenv(env_var)
        if configured_path and Path(configured_path).exists():
            return configured_path

    for binary_name in ("msedgedriver.exe", "msedgedriver"):
        driver_path = shutil.which(binary_name)
        if driver_path:
            return driver_path

    return None


def setup_driver():
    """
    Creates and configures a Microsoft Edge WebDriver instance.
    
    Returns:
        webdriver.Edge: Configured Edge WebDriver instance
    """
    options = webdriver.EdgeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver_path = _resolve_edge_driver_path()
    if driver_path:
        service = Service(driver_path)
    else:
        try:
            service = Service(EdgeChromiumDriverManager().install())
        except RequestsConnectionError as exc:
            raise RuntimeError(
                "No local Microsoft Edge WebDriver was found and the driver "
                "could not be downloaded. Install msedgedriver, add it to PATH, "
                "or set EDGE_DRIVER_PATH/MSEDGEDRIVER_PATH."
            ) from exc
    
    return webdriver.Edge(service=service, options=options)


def ensure_driver_alive(driver):
    """
    Checks if the driver is still alive and recreates it if necessary.
    
    Args:
        driver: WebDriver instance to check
        
    Returns:
        webdriver.Edge: Active WebDriver instance
    """
    try:
        driver.current_url
        return driver
    except:
        return setup_driver()


def close_driver(driver):
    """
    Closes the WebDriver instance.
    
    Args:
        driver: WebDriver instance to close
    """
    if driver:
        driver.quit()
