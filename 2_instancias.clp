(definstances instancies-generades
    ;;; --- LOCALITZACIONS ADDICIONALS ---
    ([loc501] of Localizacion (direccion "Carrer de Balmes 450") (distrito "Sarria-Sant Gervasi") (longitud 2.1384) (latitud 41.4112))
    ([loc502] of Localizacion (direccion "Avinguda Meridiana 120") (distrito "Sant Andreu") (longitud 2.1856) (latitud 41.4190))
    ([loc503] of Localizacion (direccion "Carrer de la Marina 200") (distrito "Eixample") (longitud 2.1821) (latitud 41.4012))
    ([loc504] of Localizacion (direccion "Gran Via 580") (distrito "Eixample") (longitud 2.1630) (latitud 41.3850))
    ([loc505] of Localizacion (direccion "Carrer de Sants 30") (distrito "Sants-Montjuic") (longitud 2.1412) (latitud 41.3755))
    ([loc506] of Localizacion (direccion "Passeig de Gracia 92") (distrito "Eixample") (longitud 2.1610) (latitud 41.3920))
    ([loc507] of Localizacion (direccion "Carrer de Mallorca 350") (distrito "Eixample") (longitud 2.1705) (latitud 41.3988))
    ([loc508] of Localizacion (direccion "Carrer de Piquer 12") (distrito "Sants-Montjuic") (longitud 2.1690) (latitud 41.3721))
    ([loc509] of Localizacion (direccion "Rambla del Poblenou 45") (distrito "Sant Marti") (longitud 2.2012) (latitud 41.4005))
    ([loc510] of Localizacion (direccion "Travessera de les Corts 150") (distrito "Les Corts") (longitud 2.1255) (latitud 41.3833))

    ;;; --- SERVEIS (Exemples de Col·legis i altres) ---
    ([serv_cole501] of Servicio (tipoServicio COLEGIO) (localizacion [loc501]))
    ([serv_cole502] of Servicio (tipoServicio COLEGIO) (localizacion [loc502]))
    ([serv_hosp501] of Servicio (tipoServicio HOSPITAL) (localizacion [loc504]))
    ([serv_supe501] of Servicio (tipoServicio SUPERMERCADO) (localizacion [loc505]))
    ([serv_gym501] of Servicio (tipoServicio GIMNASIO) (localizacion [loc509]))

    ;;; --- VIVENDES ---
    ([viv501] of Vivienda 
        (nombre "Penthouse with views") 
        (tipo PISO) 
        (habitaciones 3) 
        (m2 95) 
        (amueblado TRUE) 
        (localizacion [loc501]))
    ([viv502] of Vivienda 
        (nombre "Modern Studio Sant Andreu") 
        (tipo ESTUDIO) 
        (habitaciones 1) 
        (m2 45) 
        (amueblado TRUE) 
        (localizacion [loc502]))
    ([viv503] of Vivienda 
        (nombre "Family Apartment Marina") 
        (tipo PISO) 
        (habitaciones 4) 
        (m2 120) 
        (amueblado FALSE) 
        (localizacion [loc503]))
    ([viv504] of Vivienda 
        (nombre "Charming Eixample Flat") 
        (tipo PISO) 
        (habitaciones 2) 
        (m2 75) 
        (amueblado TRUE) 
        (localizacion [loc504]))
    ([viv505] of Vivienda 
        (nombre "Sants Cozy Room") 
        (tipo HABITACION) 
        (habitaciones 1) 
        (m2 15) 
        (amueblado TRUE) 
        (localizacion [loc505]))

    ;;; --- OFERTES ---
    ([ofe501] of Oferta (idOferta "OFERTA 501") (precio 1850.0) (vivienda [viv501]))
    ([ofe502] of Oferta (idOferta "OFERTA 502") (precio 850.0) (vivienda [viv502]))
    ([ofe503] of Oferta (idOferta "OFERTA 503") (precio 2100.0) (vivienda [viv503]))
    ([ofe504] of Oferta (idOferta "OFERTA 504") (precio 1450.0) (vivienda [viv504]))
    ([ofe505] of Oferta (idOferta "OFERTA 505") (precio 450.0) (vivienda [viv505]))
    ([ofe506] of Oferta (idOferta "OFERTA 506") (precio 3200.0) (vivienda [viv501]))
)