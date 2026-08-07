# Architecture

## Principle

Course notes define topic order, terminology, notation, mathematical level, and pedagogical scope.
The Streamlit application complements the notes with interaction instead of reproducing every paragraph.

## Layering

- `app.py`: entry point, common sidebar, topic routing.
- `core/`: reusable UI, formatting, question engine, and Streamlit-independent calculation/classification logic.
- `topics/`: topic-specific presentation and interactions.
- `tests/`: numerical/logic, source-consistency, axis-label, and AppTest checks.

## Chart contract

Topic modules must not call `st.plotly_chart` directly.
All Plotly charts must pass through:

```python
render_plotly(fig, x_title="...", y_title="...")
```

Both axis titles are mandatory. `tests/test_chart_axis_labels.py` enforces the contract.

## Topic 01 source mapping

The first topic follows the order of `01_veri_istatistige_giris.tex`:

1. statistical purpose and thinking flow,
2. dataset structure,
3. categorical/quantitative variables,
4. measurement levels,
5. cross-sectional/time-series distinction,
6. data sources and observational study/experiment distinction,
7. descriptive statistics/statistical inference,
8. population/sample and representativeness,
9. software role and statistical ethics,
10. integrated transportation example and general check.

No later-topic statistical methods are assumed.
