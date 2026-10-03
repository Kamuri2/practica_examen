def evaluate_rules(P: bool, Q: bool, R: bool, S: bool, V: bool, H: bool):
    """
    P: Permiso de acceso
    Q: Reporte de robo
    R: Material peligroso
    S: Inspección aprobada
    V: Vigencia de certificación del conductor (Nueva)
    H: Horario permitido (Nueva)

    Reglas originales:
    A = P and S and not Q
    E = P and (R or Q)

    Reglas ampliadas (justificadas):
    - Un camión de material peligroso (R) sólo puede entrar en horario permitido (H).
    - Un conductor requiere certificación vigente (V) para entrar, de lo contrario se niega A.
    
    Nuevas fórmulas:
    A = P and S and not Q and V and (not R or H)
    E = P and (R or Q) and (not V) # A inspección si entra sin certificación o si es E original
    """
    
    A = P and S and (not Q) and V and ((not R) or H)
    E = P and (R or Q) or (P and not V)

    explicacion = []
    if A:
        explicacion.append("Se concedió acceso (A) porque: tiene permiso (P), inspección aprobada (S), no hay reporte de robo (!Q), tiene certificación vigente (V) y cumple condición de horario/material (!R o H).")
    else:
        motivos = []
        if not P: motivos.append("no tiene permiso (P)")
        if not S: motivos.append("falló inspección (S)")
        if Q: motivos.append("tiene reporte de robo (Q)")
        if not V: motivos.append("no tiene certificación vigente (V)")
        if R and not H: motivos.append("trae material peligroso fuera de horario permitido (R y !H)")
        explicacion.append("Se denegó acceso (A) porque: " + ", ".join(motivos) + ".")

    if E:
        motivos_e = []
        if P and R: motivos_e.append("tiene permiso y trae material peligroso (P y R)")
        if P and Q: motivos_e.append("tiene permiso pero tiene reporte de robo (P y Q)")
        if P and not V: motivos_e.append("tiene permiso pero no tiene certificación vigente (P y !V)")
        explicacion.append("Se envió a inspección especial (E) porque: " + ", ".join(motivos_e) + ".")

    return A, E, " ".join(explicacion)
