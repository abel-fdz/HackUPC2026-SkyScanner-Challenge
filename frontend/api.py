import streamlit as st
from datetime import date
import requests
import time

# --- CONFIGURACIÓN ---
API_KEY = "sh782613596881417389290430162312"
BASE_URL = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search"

st.set_page_config(page_title="SkyScanner Live", page_icon="✈️")

# --- CSS ---
st.markdown("""
    <style>
    .stButton button {
        border-radius: 25px !important;
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        height: 3em;
    }
    .flight-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.2em;
        margin-bottom: 1em;
        border-left: 4px solid #0070f3;
    }
    .eco-badge {
        background: #d4edda;
        color: #155724;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PRINCIPAL API ---
def buscar_vuelos_skyscanner(origen, destino, fecha):
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"  # ← añade esta línea si no la tienes
    }
    payload = {
        "query": {
            "market": "ES",
            "locale": "es-ES",
            "currency": "EUR",
            "queryLegs": [{
                "originPlaceId": {"iata": origen},
                "destinationPlaceId": {"iata": destino},
                "date": {
                    "year": fecha.year,
                    "month": fecha.month,
                    "day": fecha.day
                }
            }],
            "adults": 1,
            "cabinClass": "CABIN_CLASS_ECONOMY",
            "includeSustainabilityData": True
        }
    }

    # 1. CREATE
    r = requests.post(f"{BASE_URL}/create", json=payload, headers=headers)
    if r.status_code != 200:
        return {"error": f"Error {r.status_code}: {r.text}"}

    data = r.json()
    session_token = data.get("sessionToken")
    if not session_token:
        return {"error": "No se obtuvo sessionToken"}

    # 2. POLL (hasta que status sea COMPLETE o máx 5 intentos)
    for _ in range(5):
        time.sleep(1.5)
        r_poll = requests.post(
            f"{BASE_URL}/poll/{session_token}",
            headers=headers
        )
        if r_poll.status_code != 200:
            return {"error": f"Error poll {r_poll.status_code}: {r_poll.text}"}
        poll_data = r_poll.json()
        if poll_data.get("status") == "RESULT_STATUS_COMPLETE":
            break

    return poll_data

# --- FUNCIÓN PARA RENDERIZAR UNA TARJETA DE VUELO DETALLADA ---
def mostrar_vuelo(itinerary_id, itinerary, content):
    results = content.get("results", {})
    legs_dict = results.get("legs", {})
    segments_dict = results.get("segments", {})
    places_dict = results.get("places", {})
    carriers_dict = results.get("carriers", {})
    agents_dict = results.get("agents", {})

    leg_ids = itinerary.get("legIds", [])
    pricing_options = itinerary.get("pricingOptions", [])
    sustainability = itinerary.get("sustainabilityData", {})

    # Mejor precio
    best_price = None
    best_option = None
    for opt in pricing_options:
        amt = opt.get("price", {}).get("amount")
        if amt:
            price_val = float(amt) / 1000  # la API devuelve en miliunidades
            if best_price is None or price_val < best_price:
                best_price = price_val
                best_option = opt

    with st.container():
        st.markdown('<div class="flight-card">', unsafe_allow_html=True)

        # Eco badge
        if sustainability.get("isEcoContender"):
            delta = sustainability.get("ecoContenderDelta", 0)
            st.markdown(f'<span class="eco-badge">🌿 Eco -{abs(delta):.0f}% CO₂</span>', unsafe_allow_html=True)

        # --- PIERNAS DEL VUELO ---
        for leg_id in leg_ids:
            leg = legs_dict.get(leg_id, {})

            orig_id = leg.get("originPlaceId", "")
            dest_id = leg.get("destinationPlaceId", "")
            orig_place = places_dict.get(orig_id, {})
            dest_place = places_dict.get(dest_id, {})

            dep = leg.get("departureDateTime", {})
            arr = leg.get("arrivalDateTime", {})
            dur = leg.get("durationInMinutes", 0)
            stops = leg.get("stopCount", 0)

            dep_str = f"{dep.get('hour',0):02d}:{dep.get('minute',0):02d}"
            arr_str = f"{arr.get('hour',0):02d}:{arr.get('minute',0):02d}"
            dur_str = f"{dur // 60}h {dur % 60}m"
            stops_str = "Directo ✅" if stops == 0 else f"{stops} escala(s) ⚠️"

            orig_iata = orig_place.get("iata", orig_id)
            dest_iata = dest_place.get("iata", dest_id)
            orig_name = orig_place.get("name", "")
            dest_name = dest_place.get("name", "")

            # Aerolíneas
            carrier_ids = leg.get("marketingCarrierIds", [])
            carrier_names = [carriers_dict.get(c, {}).get("name", c) for c in carrier_ids]
            carrier_logos = [carriers_dict.get(c, {}).get("imageUrl", "") for c in carrier_ids]

            col_a, col_b, col_c = st.columns([2, 1, 2])
            with col_a:
                st.markdown(f"### {dep_str} — **{orig_iata}**")
                st.caption(orig_name)
            with col_b:
                st.markdown(f"<div style='text-align:center;padding-top:10px'>✈️<br><small>{dur_str}</small><br><small>{stops_str}</small></div>", unsafe_allow_html=True)
            with col_c:
                st.markdown(f"### {arr_str} — **{dest_iata}**")
                st.caption(dest_name)

            # Aerolíneas con logo
            for name, logo in zip(carrier_names, carrier_logos):
                cols = st.columns([1, 5])
                if logo:
                    cols[0].image(logo, width=32)
                cols[1].write(f"**{name}**")

            # --- SEGMENTOS (tramos individuales) ---
            with st.expander("🔍 Ver segmentos del vuelo"):
                for seg_id in leg.get("segmentIds", []):
                    seg = segments_dict.get(seg_id, {})
                    seg_orig = places_dict.get(seg.get("originPlaceId", ""), {})
                    seg_dest = places_dict.get(seg.get("destinationPlaceId", ""), {})
                    seg_dep = seg.get("departureDateTime", {})
                    seg_arr = seg.get("arrivalDateTime", {})
                    seg_dur = seg.get("durationInMinutes", 0)
                    flight_num = seg.get("marketingFlightNumber", "")
                    mkt_carrier = carriers_dict.get(seg.get("marketingCarrierId", ""), {}).get("name", "")
                    op_carrier = carriers_dict.get(seg.get("operatingCarrierId", ""), {}).get("name", "")

                    st.markdown(f"""
                    **{seg_orig.get('iata','?')} → {seg_dest.get('iata','?')}** — Vuelo {flight_num}  
                    🛫 {seg_dep.get('hour',0):02d}:{seg_dep.get('minute',0):02d} → 
                    🛬 {seg_arr.get('hour',0):02d}:{seg_arr.get('minute',0):02d} 
                    ({seg_dur//60}h {seg_dur%60}m)  
                    Comercializado por: **{mkt_carrier}** | Operado por: **{op_carrier}**
                    """)

        # --- PRECIO Y OPCIONES DE COMPRA ---
        st.divider()
        price_col, btn_col = st.columns([1, 2])
        with price_col:
            if best_price:
                st.metric("💰 Precio mínimo", f"{best_price:.2f} €")

        # Todas las opciones de agentes/precios
        with st.expander(f"🏷️ Ver {len(pricing_options)} opción(es) de compra"):
            for opt in pricing_options:
                opt_price = float(opt.get("price", {}).get("amount") or 0) / 1000
                transfer_type = opt.get("transferType", "")
                is_npt = "⚠️ Billete separado" if "NPT" in transfer_type else "🎫 Billete único"

                for item in opt.get("items", []):
                    agent_id = item.get("agentId", "")
                    agent = agents_dict.get(agent_id, {})
                    agent_name = agent.get("name", agent_id)
                    agent_logo = agent.get("imageUrl", "")
                    agent_rating = agent.get("rating", 0)
                    deep_link = item.get("deepLink", "")

                    item_price = float(item.get("price", {}).get("amount") or 0) / 1000

                    ac, bc, cc = st.columns([1, 3, 2])
                    if agent_logo:
                        ac.image(agent_logo, width=40)
                    bc.markdown(f"**{agent_name}** {'⭐' * round(agent_rating)} ({agent_rating:.1f})  \n{is_npt}")
                    display_price = item_price if item_price > 0 else opt_price
                    if deep_link:
                        cc.link_button(f"Reservar {display_price:.2f}€", deep_link)

                    # Detalles de equipaje si vienen
                    fare_info = opt.get("pricingOptionFare") or {}
                    cabin_bag = fare_info.get("cabinBaggage", {})
                    checked_bag = fare_info.get("checkedBaggage", {})
                    if cabin_bag.get("assessment") and cabin_bag["assessment"] != "ASSESSMENT_UNKNOWN":
                        st.caption(f"🎒 Equipaje cabina: {cabin_bag.get('assessment')} | {cabin_bag.get('pieces',0)} pieza(s)")
                    if checked_bag.get("assessment") and checked_bag["assessment"] != "ASSESSMENT_UNKNOWN":
                        st.caption(f"🧳 Maleta facturada: {checked_bag.get('assessment')} | {checked_bag.get('pieces',0)} pieza(s)")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")


# --- UI ---
st.title("¡Hola, Usuario! ✈️")
st.subheader("Encuentra tu próximo destino en tiempo real")

col1, col2, col3 = st.columns(3)
with col1:
    origen = st.text_input("Origen (IATA)", value="BCN")
with col2:
    destino = st.text_input("Destino (IATA)", value="MAD")
with col3:
    fecha = st.date_input("¿Cuándo sales?", date.today())

if st.button("Buscar Vuelos"):
    with st.spinner("Consultando a Skyscanner..."):
        resultados = buscar_vuelos_skyscanner(origen.upper(), destino.upper(), fecha)

    if "error" in resultados:
        st.error(resultados["error"])
    else:
        content = resultados.get("content", {})
        results = content.get("results", {})
        sorting = content.get("sortingOptions", {})
        stats = content.get("stats", {}).get("itineraries", {})

        itineraries = results.get("itineraries", {})

        # Estadísticas globales
        total = stats.get("total", {})
        min_price = float(total.get("minPrice", {}).get("amount", 0)) / 1000
        count = total.get("count", 0)
        st.success(f"✅ {count} itinerarios encontrados — desde **{min_price:.2f} €**")

        # Ordenar por "cheapest" según la API
        ordered_ids = [s["itineraryId"] for s in sorting.get("cheapest", [])]

        tabs = st.tabs(["💸 Más baratos", "⚡ Más rápidos", "⭐ Mejor valorados"])

        for tab, sort_key in zip(tabs, ["cheapest", "fastest", "best"]):
            with tab:
                ordered = [s["itineraryId"] for s in sorting.get(sort_key, [])]
                shown = 0
                for itin_id in ordered:
                    if itin_id in itineraries and shown < 5:
                        mostrar_vuelo(itin_id, itineraries[itin_id], content)
                        shown += 1

        with st.expander("Ver respuesta JSON completa"):
            st.json(resultados)