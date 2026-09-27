"""Uygulama ve Sezgi sekmelerinin ortak grafik katmanı.

Grafikler üretilen Python ve R koduyla aynı veriden, aynı renk sırasıyla çizilir. ``show_figure`` bu
sekmelerde ``st.plotly_chart``'ı çağıran tek yerdir ve eksen adları olmayan grafiği reddeder.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.codegen.base import PALETTE, REFERENCE_COLORS
from core.labs.runner import LabState, plot_key
from core.labs.spec import (
    BarChart,
    CompareBarChart,
    GroupedBarChart,
    Histogram,
    LineChart,
    Operation,
    PieChart,
)

CHART_TYPES = (BarChart, GroupedBarChart, CompareBarChart, PieChart, LineChart, Histogram)


def tr_number(value: float, decimals: int = 0, percent: bool = False) -> str:
    """Türkçe sayı: ondalık virgül, tipografik eksi; yüzde işareti sayıdan önce."""

    text = f"{value:.{decimals}f}".replace(".", ",").replace("-", "−")
    return "%" + text if percent else text


def style_figure(figure: go.Figure, *, title: str, x_title: str, y_title: str, legend_title: str = "") -> go.Figure:
    figure.update_layout(
        title={"text": title, "x": 0.0, "xanchor": "left", "font": {"size": 16}},
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend_title_text=legend_title,
        separators=",.",
        template="plotly_white",
        margin={"l": 40, "r": 20, "t": 60, "b": 45},
        font={"family": "Source Sans Pro, sans-serif", "size": 14},
        hoverlabel={"font_size": 13},
    )
    return figure


def show_figure(figure: go.Figure, *, key: str | None = None) -> None:
    """Grafiği gösterir; eksen adı olmayan (pasta dışındaki) grafik hatadır."""

    has_axes = not any(isinstance(trace, go.Pie) for trace in figure.data)
    if has_axes:
        x_title = figure.layout.xaxis.title.text or ""
        y_title = figure.layout.yaxis.title.text or ""
        if not x_title.strip() or not y_title.strip():
            raise ValueError("Her grafikte yatay ve dikey eksen adı açıkça belirtilmelidir.")
    st.plotly_chart(figure, width="stretch", key=key, config={"displaylogo": False})


# --- Grafik türleri ----------------------------------------------------------------

def _bar(op: BarChart, data: pd.DataFrame) -> go.Figure:
    labels = [tr_number(value, op.decimals, op.percent) for value in data["deger"]]
    if op.horizontal:
        trace = go.Bar(
            x=data["deger"], y=data["kategori"], orientation="h", marker_color=PALETTE[0], text=labels,
            textposition="outside", cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
        figure = go.Figure(trace)
        figure.update_yaxes(autorange="reversed")
        figure.update_xaxes(rangemode="tozero")
        if op.y_range is not None:
            figure.update_xaxes(range=list(op.y_range))
        return style_figure(figure, title=op.title, x_title=op.y_label, y_title=op.x_label)
    trace = go.Bar(
        x=data["kategori"], y=data["deger"], marker_color=PALETTE[0], text=labels, textposition="outside",
        cliponaxis=False, hovertemplate="%{x}: %{text}<extra></extra>",
    )
    figure = go.Figure(trace)
    figure.update_xaxes(type="category")
    if op.y_range is not None:
        figure.update_yaxes(range=list(op.y_range))
    else:
        figure.update_yaxes(rangemode="tozero")
    return style_figure(figure, title=op.title, x_title=op.x_label, y_title=op.y_label)


def _series_bars(table: pd.DataFrame, *, stacked: bool, decimals: int, title: str, x_title: str,
                 y_title: str, legend_title: str) -> go.Figure:
    """Satırlar seriler, sütunlar yatay eksen: üretilen koddaki matrisle aynı düzen."""

    figure = go.Figure()
    categories = [str(column) for column in table.columns]
    for index, (series, row) in enumerate(table.iterrows()):
        values = row.to_numpy(dtype=float)
        figure.add_trace(
            go.Bar(
                name=str(series), x=categories, y=values, marker_color=PALETTE[index % len(PALETTE)],
                text=[tr_number(value, decimals) for value in values],
                textposition="inside" if stacked else "outside", cliponaxis=False,
                insidetextfont={"color": "white"},
                hovertemplate=f"{series}<br>%{{x}}: %{{text}}<extra></extra>",
            )
        )
    figure.update_layout(barmode="stack" if stacked else "group")
    figure.update_xaxes(type="category")
    figure.update_yaxes(rangemode="tozero")
    return style_figure(figure, title=title, x_title=x_title, y_title=y_title, legend_title=legend_title)


def _pie(op: PieChart, table: pd.DataFrame) -> go.Figure:
    values = table[op.column].to_numpy(dtype=float)
    # Plotly saat yönünün tersinde ilk dilimi ``rotation`` açısında BİTİRİR (açı 12 yönünden saat yönünde
    # ölçülür). İlk dilimin notlardaki gibi 0°'de (saat 3 yönü) BAŞLAMASI için onun açısı kadar geri dönülür.
    rotation = 90 - 360 * values[0] / values.sum()
    figure = go.Figure(
        go.Pie(
            labels=[str(label) for label in table.index], values=values, sort=False,
            direction="counterclockwise", rotation=rotation,
            marker={"colors": list(PALETTE[: len(values)]), "line": {"color": "white", "width": 1}},
            text=[tr_number(100 * value, 1, percent=True) for value in values], textinfo="label+text",
            hovertemplate="%{label}: %{text} · açı %{customdata:.1f}°<extra></extra>",
            customdata=table["aci"].to_numpy(dtype=float),
        )
    )
    figure.update_layout(showlegend=False)
    return style_figure(figure, title=op.title, x_title="", y_title="")


def _line(op: LineChart, data: pd.DataFrame) -> go.Figure:
    figure = go.Figure(
        go.Scatter(
            x=data[op.x], y=data[op.y], mode="lines+markers", line={"color": PALETTE[0], "width": 2.5},
            marker={"size": 8}, hovertemplate="%{x}: %{y}<extra></extra>",
        )
    )
    figure.update_xaxes(dtick=1)
    return style_figure(figure, title=op.title, x_title=op.x_label, y_title=op.y_label)


def _histogram(op: Histogram, data: pd.DataFrame) -> go.Figure:
    """Üretilen kodla aynı kutular: [lower, upper] aralığında ``bins`` eşit genişlikte kutu."""

    edges = np.linspace(op.lower, op.upper, op.bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    figure = go.Figure()
    for index, (column, label) in enumerate(op.columns):
        counts, _ = np.histogram(data[column].to_numpy(dtype=float), bins=edges)
        figure.add_trace(
            go.Bar(
                x=centers, y=counts, width=np.diff(edges), name=label,
                marker={"color": PALETTE[index % len(PALETTE)], "opacity": 0.6, "line": {"width": 0}},
                hovertemplate=f"{label}<br>%{{x:.2f}} civarı: %{{y}} tekrar<extra></extra>",
            )
        )
    for index, (value, label) in enumerate(op.references):
        figure.add_trace(
            go.Scatter(
                x=[value, value], y=[0, 1], mode="lines", name=label, yaxis="y2", hoverinfo="skip",
                line={"color": REFERENCE_COLORS[index % len(REFERENCE_COLORS)], "width": 2.5, "dash": "dash"},
            )
        )
    figure.update_layout(barmode="overlay", yaxis2={"overlaying": "y", "range": [0, 1], "visible": False})
    return style_figure(figure, title=op.title, x_title=op.x_label, y_title="Tekrar sayısı")


def figure_for(op: Operation, state: LabState, label=lambda name: name) -> go.Figure:
    """Bir grafik işleminin Plotly karşılığı; ``label`` seri başlıkları için Türkçe ad verir."""

    data = state.plots[plot_key(op)]
    if isinstance(op, BarChart):
        return _bar(op, data)
    if isinstance(op, GroupedBarChart):
        table = state.tables[op.table]
        legend = label(table.index.name if op.series == "satir" else table.columns.name)
        return _series_bars(data, stacked=op.stacked, decimals=op.decimals, title=op.title, x_title=op.x_label,
                            y_title=op.y_label, legend_title=legend or "")
    if isinstance(op, CompareBarChart):
        first = state.tables[op.tables[0][1]]
        return _series_bars(data, stacked=False, decimals=op.decimals, title=op.title, x_title=op.x_label,
                            y_title=op.y_label, legend_title=label(first.index.name) or "")
    if isinstance(op, PieChart):
        return _pie(op, data)
    if isinstance(op, LineChart):
        return _line(op, data)
    if isinstance(op, Histogram):
        return _histogram(op, data)
    raise TypeError(f"Grafik türü tanınmıyor: {type(op).__name__}")
