"""Uygulama sekmesinde "Kendi verini yükle" paneli: dosya yükleme, sütun seçimi ve doğrulama.

Hesap ``core.labs.kendi_veri`` ve ``core.labs.ornek`` içindedir; bu modül yalnız seçimleri toplar. Yüklenen dosya ve
ondan kurulan uygulama yalnız bu oturumun belleğinde (``st.session_state``) tutulur; ortak önbelleğe yazılmaz.

Veri kaynağı "Notlardaki örnek"e alınınca Streamlit bu paneldeki widget'ların durumunu siler. Dosya ve seçimler bu
yüzden widget dışı anahtarlarda da saklanır; öğrenci panele döndüğünde kaldığı yerden devam eder.
"""

from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Callable

import pandas as pd
import streamlit as st

from core.labs import kendi_veri as K
from core.labs.ornek import CustomChoices, CustomLab, ParamLab, custom_case, md, parameter_value
from core.labs.ornekler import get_variants
from core.labs.spec import LabSpec

NONE = "— seçilmedi —"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PRIVACY = (
    "Dosyanız yalnız bu oturumda, sunucunun belleğinde işlenir; kaydedilmez ve başkalarıyla paylaşılmaz. Kişisel veri "
    f"(ad, kimlik numarası, iletişim bilgisi) içeren dosya yüklemeyin. En çok {K.MAX_MEGABYTES} MB ve "
    f"{K.thousands(K.MAX_ROWS)} satır; ilk satırda sütun adları olmalı."
)


@st.cache_data(show_spinner=False)
def _sample_file(topic_key: str) -> bytes:
    """Örnek dosya (alternatif örneğin verisi); öğrenci verisi içermez, ortak önbellekte tutulabilir."""

    return K.sample_excel(get_variants(topic_key).custom.sample())


def _session(key: str, token: object, factory: Callable[[], object]) -> object:
    """Oturumluk önbellek: ``token`` değişmedikçe ``factory`` yeniden çalışmaz."""

    stored = st.session_state.get(key)
    if isinstance(stored, tuple) and len(stored) == 2 and stored[0] == token:
        return stored[1]
    value = factory()
    st.session_state[key] = (token, value)
    return value


# --- Seçimlerin saklanması ---------------------------------------------------------------

def _shadow(key: str) -> str:
    return f"_kalici_{key}"


def _restore(key: str) -> None:
    """Widget çizilmeden önce: durumu silinmişse (ör. veri kaynağı değişti) son seçim geri yüklenir."""

    if key not in st.session_state and _shadow(key) in st.session_state:
        st.session_state[key] = st.session_state[_shadow(key)]


def _remember(key: str) -> None:
    if key in st.session_state:
        st.session_state[_shadow(key)] = st.session_state[key]


def _file_key(topic_key: str) -> str:
    return f"{topic_key}_kendi_yuklenen"


def _types_key(topic_key: str) -> str:
    return f"{topic_key}_kendi_tur_secimleri"


def _on_upload(topic_key: str) -> None:
    """Öğrenci dosyayı değiştirince ya da kaldırınca saklanan dosya güncellenir."""

    uploaded = st.session_state.get(f"{topic_key}_kendi_dosya")
    if uploaded is None:
        _remove_file(topic_key)
    else:
        st.session_state[_file_key(topic_key)] = (uploaded.name, uploaded.getvalue())


def _remove_file(topic_key: str) -> None:
    """Dosya ve ondan okunan her şey oturum belleğinden silinir."""

    for name in ("yuklenen", "tablo", "uygulama", "ozet", "sayfalar"):
        st.session_state.pop(f"{topic_key}_kendi_{name}", None)
    _forget_choices(topic_key)


def _forget_choices(topic_key: str) -> None:
    """Yeni dosya yüklenince önceki dosyanın sütun seçimleri silinir."""

    prefix = f"{topic_key}_kendi_"
    names = ("rol_", "secim_", "ek", "sira", "sayfa", "turler", "tur_secimleri", "ayar_")
    for key in list(st.session_state.keys()):
        text = str(key)
        bare = text[len("_kalici_"):] if text.startswith("_kalici_") else text
        if bare.startswith(prefix) and bare[len(prefix):].startswith(names):
            del st.session_state[key]


# --- Öneriler -----------------------------------------------------------------------------

def _numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def _guess(role, table: K.UploadedTable, used: set[str]) -> str:
    """Önerilen sütun: kullanımına uyan ve reddedilmeyecek ilk sütun. Sayısal rolde gözlem numarası gibi görünen
    sütunlar, kimlik rolünde boş ya da tekrarlı değeri olan sütunlar önerilmez."""

    candidates = [column for column in table.columns if column not in used]
    if role.use == "sayisal":
        for column in candidates:
            if _numeric(table.frame[column]) and not K.id_like(table, column) and K.usable(table, column, "sayisal"):
                return column
    elif role.use == "kategorik":
        for column in candidates:
            series = table.frame[column]
            levels = series.map(K.clean_text).dropna().nunique()
            if not _numeric(series) and role.levels[0] <= levels <= role.levels[1] \
                    and K.usable(table, column, "kategorik"):
                return column
    else:
        for numeric in (False, True):  # önce metin, sonra 1, 2, 3, … biçiminde numara sütunu
            for column in candidates:
                series = table.frame[column]
                complete = series.notna().all() and series.nunique() == len(series)
                if complete and _numeric(series) == numeric and (not numeric or K.id_like(table, column)) \
                        and K.usable(table, column, "serbest"):
                    return column
    return NONE


# --- Panel ---------------------------------------------------------------------------------

def _render_roles(topic_key: str, custom: CustomLab, table: K.UploadedTable) -> CustomChoices:
    options = [NONE, *table.columns]
    used: set[str] = set()
    roles: dict[str, str | None] = {}
    columns = st.columns(2)
    for index, role in enumerate(custom.roles):
        key = f"{topic_key}_kendi_rol_{role.key}"
        _restore(key)
        if key not in st.session_state or st.session_state[key] not in options:
            st.session_state[key] = _guess(role, table, used) if role.required or role.suggest else NONE
        label = role.label + ("" if role.required else " (isteğe bağlı)")
        steps = ", ".join(str(step) for step in role.steps)
        value = columns[index % 2].selectbox(label, options, key=key, help=f"{role.help} Adım: {steps}.")
        _remember(key)
        roles[role.key] = None if value == NONE else value
        if value != NONE:
            used.add(value)
    extra: tuple[str, ...] = ()
    if custom.extra_columns:
        key = f"{topic_key}_kendi_ek"
        _restore(key)
        remaining = [column for column in table.columns if column not in used]
        if key in st.session_state:
            st.session_state[key] = [column for column in st.session_state[key] if column in remaining]
        else:  # ilk açılışta kullanılabilir sütunlar
            st.session_state[key] = [column for column in remaining if K.usable(table, column, "serbest")][:K.MAX_EXTRA]
        extra = tuple(st.multiselect("Veri tablosuna eklenecek diğer sütunlar (isteğe bağlı)", remaining, key=key,
                                     placeholder="Sütun seçin"))
        _remember(key)
    order = "alfabetik"
    if any(roles.get(role) for role in custom.order_roles):
        key = f"{topic_key}_kendi_sira"
        _restore(key)
        order = st.selectbox(
            "Kategori sırası", list(K.ORDER_RULES), format_func=K.ORDER_RULES.get, key=key,
            help="Tablolarda ve grafiklerde kategorilerin sırası. Sıralı (ordinal) bir değişkende doğal sırayı "
                 "dosyadaki sırayla verebilirsiniz.",
        )
        _remember(key)
    return CustomChoices(roles=roles, extra=extra, order=order)


def _render_picks(topic_key: str, custom: CustomLab, case) -> dict[str, str]:
    picks: dict[str, str] = {}
    for role in custom.roles:
        if not role.pick or role.key not in case.roles:
            continue
        categories = list(case.orders[case.roles[role.key]])
        key = f"{topic_key}_kendi_secim_{role.key}"
        _restore(key)
        if st.session_state.get(key) not in categories:
            st.session_state[key] = case.levels[role.key]
        picks[role.key] = st.selectbox(f"{role.pick} · {md(case.labels[case.roles[role.key]])}", categories, key=key)
        _remember(key)
    return picks


def _render_settings(topic_key: str, custom: CustomLab, case, scope: object) -> dict[str, int]:
    """Tam sayı ayarları (ör. sınıf sayısı) kaydırıcıyla seçilir; başlangıç değeri veriden önerilen değerdir. Veri
    değişince (dosya, Excel sayfası ya da rollerin dosyadaki sütunları; hepsi ``scope`` içinde) öneri yeniden
    hesaplanır."""

    values: dict[str, int] = {}
    digest = hashlib.md5(repr(scope).encode("utf-8")).hexdigest()[:12]
    for setting in custom.settings:
        key = f"{topic_key}_kendi_ayar_{setting.key}_{digest}"
        _restore(key)
        stored = st.session_state.get(key)
        if not isinstance(stored, int) or not setting.minimum <= stored <= setting.maximum:
            st.session_state[key] = int(case.extra["settings"][setting.key])
        steps = ", ".join(str(step) for step in setting.steps)
        values[setting.key] = int(st.slider(setting.label, setting.minimum, setting.maximum, key=key,
                                            help=f"{setting.help} Adım: {steps}." if steps else setting.help))
        _remember(key)
    return values


def _render_types(topic_key: str, custom: CustomLab, case, table: K.UploadedTable) -> dict[str, str]:
    """Konu 1: öğrenci her sütunun istatistiksel türünü seçer; öneri sütunun içeriğinden gelir. Türü rolüyle belli
    olan sütunlar (ör. kimlik) tabloda yer almaz."""

    role_of = {column: key for key, column in case.roles.items()}
    roles = {role.key: role for role in custom.roles}
    stored: dict[str, str] = st.session_state.setdefault(_types_key(topic_key), {})
    rows, fixed = [], []
    for name, original in case.labels.items():
        if name not in case.data.columns:
            continue
        role = roles.get(role_of.get(name, ""))
        if role is not None and role.fixed_type:
            fixed.append(f"“{md(original)}” sütununun türü rolü gereği “{role.fixed_type}”.")
            continue
        guess = custom.guess_type(table.frame[original], role.key if role else None) if custom.guess_type else ""
        choice = stored.get(original, guess)
        rows.append({"Sütun": original, "Rol": role.label if role else "Veri tablosu",
                     "İstatistiksel tür": choice if choice in custom.type_choices else guess})
    st.markdown("**Adım 2 için: her sütunun istatistiksel türü**")
    st.caption("Öneri sütunun içeriğinden gelir. Tür yazılımdan değil, değişkenin anlamından gelir; gerekirse "
               "değiştirin. " + " ".join(fixed))
    digest = hashlib.md5(repr([(row["Sütun"], row["Rol"]) for row in rows]).encode("utf-8")).hexdigest()[:12]
    edited = st.data_editor(
        pd.DataFrame(rows, columns=["Sütun", "Rol", "İstatistiksel tür"]),
        column_config={
            "İstatistiksel tür": st.column_config.SelectboxColumn(options=list(custom.type_choices), required=True),
        },
        disabled=["Sütun", "Rol"],
        hide_index=True,
        width="stretch",
        key=f"{topic_key}_kendi_turler_{digest}",
    )
    chosen = dict(zip(edited["Sütun"], edited["İstatistiksel tür"]))
    stored.update(chosen)
    return chosen


def _current_file(topic_key: str, uploaded) -> tuple[str, bytes] | None:
    """Kullanılan dosya: yükleyicideki dosya ya da (yükleyicinin durumu silindiyse) saklanan son dosya."""

    if uploaded is not None:
        current = (uploaded.name, uploaded.getvalue())
        if st.session_state.get(_file_key(topic_key)) != current:
            st.session_state[_file_key(topic_key)] = current
        return current
    return st.session_state.get(_file_key(topic_key))


def render_params(topic_key: str, params: ParamLab) -> LabSpec | None:
    """Dosyasız konularda (Konu 9–12) "Kendi değerlerini gir" paneli: her parametre bir sayı girişidir. Geçerli
    değerlerle kurulan uygulamayı döndürür (yoksa ``None``); değerler kaynak değişse de oturumda korunur."""

    st.markdown(params.intro)
    groups = params.groups or ("",)
    values: dict[str, int | float] = {}
    with st.container(border=True):
        for column, group in zip(st.columns(len(groups)), groups):
            if group:
                column.markdown(f"**{group}**")
            for parameter in params.parameters:
                if parameter.group != (group if params.groups else parameter.group):
                    continue
                key = f"{topic_key}_kendi_param_{parameter.key}"
                _restore(key)
                integer = parameter.decimals == 0
                stored = st.session_state.get(key)
                if not isinstance(stored, (int, float)) or not parameter.minimum <= stored <= parameter.maximum:
                    st.session_state[key] = parameter_value(parameter)
                steps = ", ".join(str(step) for step in parameter.steps)
                value = column.number_input(
                    parameter.label,
                    min_value=int(parameter.minimum) if integer else float(parameter.minimum),
                    max_value=int(parameter.maximum) if integer else float(parameter.maximum),
                    step=int(parameter.step) if integer else float(parameter.step),
                    format="%d" if integer else f"%.{parameter.decimals}f",
                    key=key,
                    help=f"{parameter.help} Adım: {steps}." if steps else parameter.help or None,
                )
                _remember(key)
                values[parameter.key] = parameter_value(parameter, value)
        try:
            if params.validate is not None:
                params.validate(values)
            spec = _session(f"{topic_key}_kendi_param_uygulama", tuple(sorted(values.items())),
                            lambda: params.build(values))
        except K.UploadError as error:
            st.error(md(str(error)), icon=":material/error:")
            return None
    return spec


def render_custom(topic_key: str, custom: CustomLab) -> LabSpec | None:
    """Veri panelini gösterir; geçerli seçimlerle kurulan uygulamayı döndürür (yoksa ``None``)."""

    st.markdown(custom.intro)
    st.caption(PRIVACY)
    left, right = st.columns([4, 1], vertical_alignment="bottom")
    uploaded = left.file_uploader("Veri dosyası (.xlsx ya da .csv)", type=["xlsx", "csv"],
                                  key=f"{topic_key}_kendi_dosya", max_upload_size=K.MAX_MEGABYTES,
                                  on_change=_on_upload, args=(topic_key,))
    right.download_button(
        "Örnek dosya", data=_sample_file(topic_key), file_name=f"ikt217_{topic_key}_ornek.xlsx", mime=XLSX_MIME,
        key=f"{topic_key}_kendi_ornek", icon=":material/download:", width="stretch",
        help="Alternatif örneğin verisi. İndirip yükleyerek seçenekleri deneyebilirsiniz.",
    )
    current = _current_file(topic_key, uploaded)
    if current is None:
        st.info("Başlamak için bir dosya yükleyin. Biçimi görmek için örnek dosyayı indirip yükleyebilirsiniz.",
                icon=":material/upload_file:")
        return None
    name, data = current
    if uploaded is None:
        note, button = st.columns([4, 1], vertical_alignment="center")
        note.caption(f"Kullanılan dosya: {md(name)}. Başka bir dosya yükleyerek değiştirebilirsiniz.")
        button.button("Dosyayı kaldır", key=f"{topic_key}_kendi_kaldir", on_click=_remove_file, args=(topic_key,),
                      icon=":material/delete:", width="stretch")
    digest = hashlib.md5(data).hexdigest()
    token = (digest, name)
    if st.session_state.get(f"{topic_key}_kendi_ozet") != token:
        _forget_choices(topic_key)
        st.session_state[f"{topic_key}_kendi_ozet"] = token
    try:
        sheet = None
        if name.lower().endswith(".xlsx"):
            sheets = _session(f"{topic_key}_kendi_sayfalar", token, lambda: K.excel_sheets(data))
            if len(sheets) > 1:
                key = f"{topic_key}_kendi_sayfa"
                _restore(key)
                sheet = st.selectbox("Sayfa", sheets, key=key)
                _remember(key)
        table = _session(f"{topic_key}_kendi_tablo", (token, sheet), lambda: K.read_upload(name, data, sheet))
    except K.UploadError as error:
        st.error(md(str(error)), icon=":material/error:")
        return None
    with st.expander(f"Dosyanın ilk satırları ({len(table.frame)} satır, {len(table.columns)} sütun)"):
        st.dataframe(table.frame.head(8), hide_index=True)
    for note in table.notes:
        st.caption(md(note))
    with st.container(border=True):
        st.markdown("**Sütunları seçin**")
        try:
            choices = _render_roles(topic_key, custom, table)
            case, notes = custom_case(custom, table, choices)
            picks = _render_picks(topic_key, custom, case)
            types = _render_types(topic_key, custom, case, table) if custom.type_choices else {}
            scope = (token, sheet, tuple(sorted(choices.roles.items(), key=str)))
            settings = _render_settings(topic_key, custom, case, scope) if custom.settings else {}
            if picks or types or settings:
                choices = replace(choices, picks=picks, types=types, settings=settings)
                case, notes = custom_case(custom, table, choices)
            key = (token, sheet, tuple(sorted(choices.roles.items(), key=str)), choices.extra, choices.order,
                   tuple(sorted(choices.picks.items())), tuple(sorted(choices.types.items())),
                   tuple(sorted(choices.settings.items())))
            spec = _session(f"{topic_key}_kendi_uygulama", key, lambda: custom.build(case))
        except K.UploadError as error:
            st.error(md(str(error)), icon=":material/error:")
            return None
        except Exception as error:  # beklenmeyen veri: öğrenciye anlaşılır bir ileti, ayrıntı türüyle
            st.error(f"Dosya bu seçimlerle işlenemedi ({type(error).__name__}: {md(str(error))}). Seçimleri "
                     "değiştirin ya da dosyayı kontrol edin.", icon=":material/error:")
            return None
    for note in notes:
        st.caption(md(note))
    return spec
