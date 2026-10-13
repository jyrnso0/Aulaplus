# AulaPlus · 

**Curso:** Componentes en Lógica de Negocios · Unidad 3

**Institución:** Facultad de Ingeniería Mecánica y Eléctrica (FIME), Universidad Autónoma de Nuevo León

**Profesor:** Miguel Ángel Gómez Marroquín

**Caso:** AulaPlus (Caso 08)

**Fecha de entrega:** 13 de octubre de 2026

## Equipo

| Integrante | Matrícula 
|---|---|
| Ángel Adrián Velez Contreras | [2145646] 
| Alonso Morales Quintanilla | [2145757] 
| Jairany López Ramos | [2145407] 

## Qué es este repositorio

Parte de los requerimientos de la Unidad 2 (BRD, historias de usuario, glosario y BPMN) y llega a una arquitectura
en tres capas, Aplicación, Dominio e Infraestructura, con cada decisión justificada, trazable a una regla de negocio
y revisada con SOLID. La arquitectura gira alrededor de **Domain Model**, con **Service Layer**, **Repository**,
**Unit of Work** y **CQRS** lógico sobre una sola base de datos.

Reglas que más pesan en el diseño: BR-0001 (pago en 15 minutos), BR-0004 (penalización del 50% con menos de 4 horas),
BR-0005 (comisión 20% y 80% al tutor), BR-0006 (sin traslapes), BR-0007 (disputa en 24 horas), BR-0011 (resolución en
48 horas), BR-0018 (suspensión por ausencias) y BR-0020 (no se cierra una disputa sin evidencia).

## Estructura del repositorio

```
.
├── README.md                          este archivo
├── .gitignore
├── pytest.ini
├── docs/
│   ├── 01_Informe_de_arquitectura_AulaPlus.pdf     
│   ├── 04_Matriz_de_trazabilidad.docx              
│   ├── 05_Bitacora_de_IA.docx                      
│   ├── ADR_y_Service_Layer.docx                    
│   ├── Guia_de_trabajo_AulaPlus.docx               
│   ├── etapas/
│   │   ├── Etapa_2_Seleccion_del_patron.docx
│   │   ├── Etapa_3_Mapa_de_dominio.docx
│   │   ├── Etapa_5_Repository_y_Unit_of_Work.docx
│   │   ├── Etapa_6_Commands_y_Queries.docx
│   │   └── Etapa_7_Hallazgos_SOLID.docx
├── diagrams/
│   ├── exportaciones/
│       ├── 02_Diagrama_de_clases.{pdf}
│       ├── 03_Secuencia_DS01_Resolver_disputa.{pdf}
│       └── 03_Secuencia_DS02_Reserva_y_pago.{pdf}
│   ├── fuentes/
│       ├── 02_Diagrama_de_clases.{mmd}
│       ├── 03_Secuencia_DS01_Resolver_disputa.{mmd}
│       └── 03_Secuencia_DS02_Reserva_y_pago.{mmd}
├── src/aulaplus/                      código base: aplicacion/, dominio/, infraestructura/
└── tests/                             pruebas de DS-01, DS-02, dominio y CQRS
```

## Cómo revisarlo

**Orden de lectura recomendado**

1. `docs/01_Informe_de_arquitectura_AulaPlus.pdf`: resume todas las etapas en 12 páginas.
2. `diagrams/`: el diagrama de clases y los dos de secuencia, que usan los mismos componentes.
3. `docs/04_Matriz_de_trazabilidad.docx`: comprueba que cada decisión responde a una regla.
4. `src/` y `tests/`: ejecuta las pruebas y compara con los diagramas.
5. `docs/05_Bitacora_de_IA.docx`: muestra cómo se usó la IA y qué se corrigió.

**Qué revisar y dónde, por etapa**

| Etapa | Qué se decidió | Dónde verlo |
|---|---|---|
| 1. Preparar el caso | CU-01 a CU-04 como casos base | Informe, sección 1; `docs/Guia_de_trabajo_AulaPlus.docx` |
| 2. Patrón de lógica de negocio | Domain Model frente a Transaction Script y Table Module | `docs/etapas/Etapa_2_...`; Informe, sección 2 |
| 3. Mapa de dominio | 5 aggregates, value objects, servicios de dominio y eventos | `docs/etapas/Etapa_3_...`; `diagrams/02_Mapa_de_dominio.*`; Informe, sección 3 |
| 4. Service Layer | Servicios de aplicación delgados, contratos y errores tipados | `docs/ADR_y_Service_Layer.docx`; Informe, sección 4 |
| 5. Repository y Unit of Work | Un repositorio por raíz; transacción con `begin`, `commit` y `rollback` | `docs/etapas/Etapa_5_...`; Informe, secciones 5 y 6 |
| 6. CQRS | 2 Commands y 2 Queries sobre la misma base | `docs/etapas/Etapa_6_...`; Informe, sección 7 |
| 7. SOLID | 5 hallazgos con evidencia, impacto y cambio | `docs/etapas/Etapa_7_Hallazgos_SOLID.docx`; Informe, sección 8 |
| 8. Representar y documentar | Diagrama de clases, DS-01, DS-02 y 7 ADR | `diagrams/`; `docs/ADR_y_Service_Layer.docx`; Informe, secciones 9 y 10 |
| 9. Validar | Matriz de trazabilidad y casos límite | `docs/04_Matriz_de_trazabilidad.docx`; Informe, sección 11 |

**Los diagramas de secuencia**

- `DS-02` es el flujo principal: reserva y confirmación de pago (CU-01) en una sola transacción.
- `DS-01` es el flujo con una regla: resolver una disputa sin evidencia (BR-0020), con la alternativa `alt`.
- Cada diagrama tiene su fuente `.mmd` (Mermaid) y sus exportaciones en PDF. El `.mmd` se puede abrir en https://mermaid.live pegando su contenido.

## Código base

Esqueleto en Python que representa la arquitectura: una carpeta por capa y el código mínimo de cada componente del diagrama
de clases, con los mismos nombres. La base de datos y el proveedor de pagos están simulados.

```bash
pip install pytest
pytest            # 16 pruebas, desde la raíz del repositorio
```

Las pruebas recorren DS-02 y DS-01, incluido el rollback cuando algo falla, y comprueban las reglas BR-0004, BR-0005,
BR-0006, BR-0014, BR-0018 y BR-0020, además de que el DTO de lectura del perfil del tutor no expone datos internos.

## Uso de IA

La IA se usó para borradores de alternativas, mapa de dominio, firmas de servicios, separación CQRS, revisión SOLID y
diagramas. El equipo verificó cada resultado contra la Unidad 2 y corrigió o descartó varias sugerencias. Por ejemplo,
se rechazó calcular el reembolso dentro del Application Service y se descartó separar físicamente las bases de lectura
y escritura. El detalle está en `docs/05_Bitacora_de_IA.docx`.

## Pendientes y límites declarados

- **Decisiones de negocio por validar:** extremos exactos de los plazos de pago y de disputa; destino y cobro de la
  penalización del 50%; qué ocurre si Soporte supera las 48 horas; criterio de redondeo de importes; escala y moderación
  de calificaciones; métricas y latencia del dashboard.
- **Código base:** `cancelarSesion` no calcula el monto a devolver; no hay exclusión de agenda por tutor (ADR-03) ni
  clave de idempotencia (ADR-06); CU-06 a CU-13 quedan fuera del esqueleto.
- **Propuesta SOLID-O:** convertir `PoliticaDeReembolso` en una interfaz con una implementación por causa; está
  marcada como propuesta.


