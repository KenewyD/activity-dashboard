"""
Tableau de Bord de Suivi d'Activité – Santé au Travail
Application Streamlit avec visualisations interactives
Auteure : Kenewy Diallo
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Tableau de Bord – Santé au Travail",
    page_icon="📊",
    layout="wide",
)

# ── Données de démonstration ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    np.random.seed(42)

    # Activité mensuelle 2024
    mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
            "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    activite = pd.DataFrame({
        "mois": mois,
        "visites_programmees": [98, 102, 115, 108, 120, 95, 80, 60, 118, 122, 110, 105],
        "visites_realisees":   [92,  96, 109, 101, 114, 89, 75, 55, 112, 116, 103,  98],
        "visites_urgentes":    [ 5,   4,   7,   6,   8,  4,  3,  2,   6,   7,   5,   4],
    })
    activite["taux_realisation"] = (
        activite["visites_realisees"] / activite["visites_programmees"] * 100
    ).round(1)

    # Adhérents par secteur
    secteurs = pd.DataFrame({
        "secteur": ["Services", "Industrie", "BTP", "Santé", "Commerce"],
        "nb_adherents": [142, 98, 67, 54, 89],
        "score_engagement": [72, 65, 58, 81, 63],
    })

    # Risques identifiés
    risques = pd.DataFrame({
        "type_risque": ["TMS", "Risques psychosociaux", "Bruit", "Chimique", "Chutes"],
        "nb_cas": [187, 134, 89, 56, 43],
    })

    return activite, secteurs, risques

activite, secteurs, risques = load_data()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📊 Tableau de Bord – Suivi d'Activité Santé au Travail")
st.markdown("*Pilotage en temps réel de l'activité médicale et des indicateurs clés.*")
st.divider()

# ── Filtres ──────────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    periode = st.select_slider(
        "📅 Période (mois)",
        options=activite["mois"].tolist(),
        value=("Jan", "Déc"),
    )
with col_f2:
    secteur_filtre = st.multiselect(
        "🏭 Secteurs",
        options=secteurs["secteur"].tolist(),
        default=secteurs["secteur"].tolist(),
    )

# Filtrage
idx_debut = activite["mois"].tolist().index(periode[0])
idx_fin   = activite["mois"].tolist().index(periode[1]) + 1
activite_filtree = activite.iloc[idx_debut:idx_fin]
secteurs_filtres = secteurs[secteurs["secteur"].isin(secteur_filtre)]

st.divider()

# ── KPI ──────────────────────────────────────────────────────────────────────
st.subheader("🎯 Indicateurs Clés")

total_realisees   = activite_filtree["visites_realisees"].sum()
total_programmees = activite_filtree["visites_programmees"].sum()
taux_moy          = activite_filtree["taux_realisation"].mean().round(1)
total_urgentes    = activite_filtree["visites_urgentes"].sum()
total_adherents   = secteurs_filtres["nb_adherents"].sum()
engagement_moy    = secteurs_filtres["score_engagement"].mean().round(1)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("✅ Visites réalisées",   f"{total_realisees:,}")
k2.metric("📅 Visites programmées", f"{total_programmees:,}")
k3.metric("📈 Taux de réalisation", f"{taux_moy}%",
          delta=f"{taux_moy - 90:.1f}% vs objectif 90%",
          delta_color="normal")
k4.metric("🚨 Visites urgentes",    f"{total_urgentes}")
k5.metric("🏢 Adhérents",           f"{total_adherents:,}")
k6.metric("💡 Score engagement",    f"{engagement_moy}/100")

st.divider()

# ── Graphiques ligne 1 ───────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Activité mensuelle")
    fig1 = go.Figure()
    fig1.add_bar(
        x=activite_filtree["mois"],
        y=activite_filtree["visites_programmees"],
        name="Programmées",
        marker_color="#CBD5E1",
    )
    fig1.add_bar(
        x=activite_filtree["mois"],
        y=activite_filtree["visites_realisees"],
        name="Réalisées",
        marker_color="#3B82F6",
    )
    fig1.update_layout(
        barmode="overlay",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=20, b=0),
        height=320,
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📈 Taux de réalisation (%)")
    fig2 = px.line(
        activite_filtree,
        x="mois",
        y="taux_realisation",
        markers=True,
        color_discrete_sequence=["#3B82F6"],
    )
    fig2.add_hline(
        y=90,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text="Objectif 90%",
    )
    fig2.update_layout(
        yaxis_range=[70, 105],
        margin=dict(t=20, b=0),
        height=320,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Graphiques ligne 2 ───────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏭 Adhérents par secteur")
    fig3 = px.pie(
        secteurs_filtres,
        values="nb_adherents",
        names="secteur",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.4,
    )
    fig3.update_layout(margin=dict(t=20, b=0), height=320)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("⚠️ Risques professionnels identifiés")
    fig4 = px.bar(
        risques.sort_values("nb_cas"),
        x="nb_cas",
        y="type_risque",
        orientation="h",
        color="nb_cas",
        color_continuous_scale="Blues",
    )
    fig4.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=20, b=0),
        height=320,
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Score engagement par secteur ─────────────────────────────────────────────
st.subheader("💡 Score d'engagement par secteur")
fig5 = px.bar(
    secteurs_filtres.sort_values("score_engagement", ascending=False),
    x="secteur",
    y="score_engagement",
    color="score_engagement",
    color_continuous_scale="Blues",
    text="score_engagement",
)
fig5.add_hline(y=70, line_dash="dash", line_color="#EF4444", annotation_text="Seuil cible 70")
fig5.update_traces(texttemplate="%{text}", textposition="outside")
fig5.update_layout(
    yaxis_range=[0, 100],
    coloraxis_showscale=False,
    margin=dict(t=20),
    height=320,
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.caption("📊 Données de démonstration – Tableau de bord développé avec Python & Streamlit | Kenewy Diallo")
