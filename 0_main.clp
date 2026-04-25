(defmodule MAIN (export ?ALL))

(load "1_ontologia.clp")
(load "2_instancias.clp")
(load "3_entrada.clp")
(load "4_abstraccion.clp")
(load "5_heuristica.clp")
(load "6_refinamiento.clp")
(load "7_salida.clp")

(reset)
(focus entrada)
(run)
(exit)