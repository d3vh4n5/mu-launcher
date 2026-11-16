"""
Sección de noticias del launcher: las últimas noticias de la web en una línea
cada una (categoría, título y fecha). Un clic abre la noticia completa en la web.

El fondo ocupa todo el ancho de la ventana; el contenido queda alineado con los
botones (components_width), centrado.
"""
import tkinter.font as tkfont
import webbrowser
from datetime import datetime
from tkinter import Frame, Label

from const.config import app_width, components_width, NEWS_REFRESH_MS
from const.texts import TEXTS
from services.api_service import ServerService
from utils.logger import logger
from utils.periodic import run_periodically
from utils.state import AppState

MAX_ITEMS = 4
BOX_HEIGHT = 132
BOX_BG = "#0d0716"
ROW_HOVER_BG = "#1c1230"
TITLE_FG = "#e8e8e8"
DIM_FG = "#8c8c8c"
CATEGORY_COLORS = {"novedad": "#2ecc71", "evento": "#ffa500", "mantenimiento": "#ff4d4d"}

TAG_WIDTH = 46   # px reservados para la categoría
DATE_WIDTH = 34  # px reservados para la fecha (dd/mm)
# Margen lateral para que el contenido mida lo mismo que los botones
ROW_PADX = (app_width - components_width) // 2


def _short_date(iso):
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone().strftime("%d/%m")
    except Exception:
        return ""


def _fit(text, font, max_px):
    """Recorta el texto con "…" para que entre en max_px."""
    if font.measure(text) <= max_px:
        return text
    while text and font.measure(text + "…") > max_px:
        text = text[:-1]
    return text.rstrip() + "…"


def _open(url):
    if url:
        webbrowser.open(url)


def load_frame_news(parent, state: AppState):
    def txt(key, fallback=""):
        return TEXTS.get(state.lang.get(), TEXTS["Spn"]).get(key, fallback)

    # Alto fijo: "cargando", "sin noticias" y la lista ocupan lo mismo (no salta el resto)
    box = Frame(parent, width=app_width, height=BOX_HEIGHT, bg=BOX_BG)
    box.pack_propagate(False)
    box.pack(fill="x")

    header = Frame(box, bg=BOX_BG)
    header.pack(fill="x", padx=ROW_PADX, pady=(10, 4))
    lbl_title = Label(header, text=txt("news_title", "Noticias"), bg=BOX_BG, fg="white",
                      font=("Arial", 9, "bold"))
    lbl_title.pack(side="left")
    lbl_all = Label(header, text=txt("news_all", "Ver todas"), bg=BOX_BG, fg="dodger blue",
                    font=("Arial", 8, "underline"), cursor="hand2")
    # Se muestra cuando la API informa la URL de la sección de noticias

    body = Frame(box, bg=BOX_BG)
    body.pack(fill="x", pady=(0, 6))

    title_font = tkfont.Font(family="Arial", size=9)
    tag_font = tkfont.Font(family="Arial", size=7, weight="bold")
    date_font = tkfont.Font(family="Arial", size=8)
    title_px = components_width - TAG_WIDTH - DATE_WIDTH - 8

    last = {"data": None, "status": "loading"}

    def clear_body():
        for child in body.winfo_children():
            child.destroy()

    def show_message(key, fallback):
        clear_body()
        Label(body, text=txt(key, fallback), bg=BOX_BG, fg=DIM_FG,
              font=("Arial", 8), anchor="w").pack(fill="x", padx=ROW_PADX, pady=2)

    def add_row(item):
        url = item.get("url")
        row = Frame(body, bg=BOX_BG, cursor="hand2" if url else "")
        row.pack(fill="x", padx=ROW_PADX, pady=2)

        category = item.get("category", "")
        tag = Label(row, text=txt(f"cat_{category}", category.upper()[:6]), bg=BOX_BG,
                    fg=CATEGORY_COLORS.get(category, DIM_FG), font=tag_font, anchor="w")
        tag.place(x=0, rely=0.5, anchor="w", width=TAG_WIDTH)

        title = Label(row, text=_fit(str(item.get("title", "")), title_font, title_px),
                      bg=BOX_BG, fg=TITLE_FG, font=title_font, anchor="w")
        title.place(x=TAG_WIDTH, rely=0.5, anchor="w", width=title_px + 4)

        date = Label(row, text=_short_date(item.get("publishedAt") or ""), bg=BOX_BG,
                     fg=DIM_FG, font=date_font, anchor="e")
        date.place(relx=1.0, rely=0.5, anchor="e", width=DATE_WIDTH)

        row.configure(height=title_font.metrics("linespace") + 4)
        widgets = (row, tag, title, date)

        def set_bg(color):
            for widget in widgets:
                widget.configure(bg=color)

        for widget in widgets:
            widget.bind("<Enter>", lambda e: set_bg(ROW_HOVER_BG))
            widget.bind("<Leave>", lambda e: set_bg(BOX_BG))
            widget.bind("<Button-1>", lambda e, u=url: _open(u))

    def render():
        data = last["data"]
        if last["status"] == "loading":
            show_message("news_loading", "Cargando noticias...")
            return
        if data is None:
            show_message("news_error", "No se pudieron cargar las noticias")
            return

        items = data.get("items", [])[:MAX_ITEMS]
        if not items:
            show_message("news_empty", "No hay noticias por ahora")
        else:
            clear_body()
            for item in items:
                add_row(item)

        news_url = data.get("newsUrl")
        if news_url:
            lbl_all.bind("<Button-1>", lambda e: _open(news_url))
            lbl_all.pack(side="right")

    def on_loaded(data):
        # En un refresco fallido se conservan las noticias que ya se mostraban
        if data is None and last["data"] is not None:
            return
        if data == last["data"] and last["status"] == "done":
            return  # sin cambios: no se redibuja (evita parpadeo)
        last["data"] = data
        last["status"] = "done"
        render()

    def update_lang(*args):
        lbl_title.config(text=txt("news_title", "Noticias"))
        lbl_all.config(text=txt("news_all", "Ver todas"))
        render()

    state.lang.trace_add("write", update_lang)
    render()
    # Primera carga enseguida y después cada NEWS_REFRESH_MS
    run_periodically(box, NEWS_REFRESH_MS, lambda: ServerService().fetch_news(), on_loaded,
                     first_delay_ms=0, name="news-fetch")
    logger.debug("Cargando noticias del launcher")
