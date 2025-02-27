"""The PanelFrontend and AppStateWatcher make it easy to create Lightning Apps with the Panel data app
framework."""
from lightning_app.frontend.panel.app_state_watcher import AppStateWatcher
from lightning_app.frontend.panel.panel_frontend import PanelFrontend

__all__ = ["PanelFrontend", "AppStateWatcher"]
