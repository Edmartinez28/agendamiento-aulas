/* =========================================================================
   Rejilla de la semana · lógica compartida
   =========================================================================

   La usan el horario del aula (gestion) y el horario personal (cuentas). Las
   dos pintan lunes–viernes × franjas, resaltan la columna de hoy, filtran por
   estado y navegan semanas con ?week=YYYY-MM-DD. Lo único que cambia entre
   ellas es QUÉ dice cada bloque, y eso lo decide quien la monta.

   Todas las fechas se construyen en hora local (new Date(a, m, d)), nunca
   parseando el ISO directamente: hacerlo en UTC desplaza un día a Ecuador.

   Uso:
     RejillaSemana.montar({
       cuerpo: <tbody>, slots: [...], reservas: [...], inicioSemana: "2026-07-27",
       bloque: function (r) { return { titulo, sub, nota }; },
       alAbrir: function (r) { ... },        // opcional
       alPintar: function (lista) { ... }    // opcional, para métricas
     });
   ========================================================================= */

(function (global) {
    "use strict";

    function aFecha(iso) {
        var p = String(iso).split("-");
        return new Date(parseInt(p[0], 10), parseInt(p[1], 10) - 1, parseInt(p[2], 10));
    }

    function aIso(fecha) {
        return fecha.getFullYear() + "-" +
            String(fecha.getMonth() + 1).padStart(2, "0") + "-" +
            String(fecha.getDate()).padStart(2, "0");
    }

    // Lunes = 0 … Viernes = 4. Sábado y domingo no tienen columna: una reserva
    // en fin de semana simplemente no se pinta, no revienta la rejilla.
    function indiceDia(iso) {
        var dia = aFecha(iso).getDay();
        return (dia === 0 || dia === 6) ? null : dia - 1;
    }

    function hora(t) { return String(t || "").substring(0, 5); }

    function escapar(texto) {
        return String(texto == null ? "" : texto)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;")
            .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    function textoLargo(iso) {
        return aFecha(iso).toLocaleDateString("es-EC", {
            day: "numeric", month: "long", year: "numeric"
        });
    }

    function montar(op) {
        var cuerpo = op.cuerpo;
        var slots = op.slots || [];
        var reservas = op.reservas || [];
        var lunes = aFecha(op.inicioSemana);
        var hoyIso = aIso(new Date());
        var indiceHoy = -1;

        // Fecha de cada columna y marca de la de hoy
        for (var d = 0; d < 5; d++) {
            var fecha = new Date(lunes.getFullYear(), lunes.getMonth(), lunes.getDate() + d);
            var etiqueta = document.querySelector('[data-fecha-dia="' + d + '"]');
            if (etiqueta) {
                etiqueta.textContent = String(fecha.getDate()).padStart(2, "0") + "/" +
                    String(fecha.getMonth() + 1).padStart(2, "0");
            }
            if (aIso(fecha) === hoyIso) {
                indiceHoy = d;
                var cabecera = document.querySelector('th[data-dia="' + d + '"]');
                if (cabecera) cabecera.classList.add("hoy");
            }
        }

        function dibujarBloque(reserva) {
            var partes = op.bloque(reserva) || {};

            return '<button type="button" class="bloque" data-estado="' + escapar(reserva.estado) + '" ' +
                   'data-reserva="' + escapar(reserva.id) + '">' +
                   '<span class="bloque__titulo">' + escapar(partes.titulo) + '</span>' +
                   (partes.sub ? '<span class="bloque__sub">' + escapar(partes.sub) + '</span>' : '') +
                   '<span class="bloque__pie">' +
                       '<span class="bloque__estado">' + escapar(reserva.estado) + '</span>' +
                       (partes.nota ? '<span>' + escapar(partes.nota) + '</span>' : '') +
                   '</span>' +
                   '</button>';
        }

        function pintar(lista) {
            cuerpo.innerHTML = "";

            // Índice franja → día → reservas
            var rejilla = {};
            slots.forEach(function (s) {
                rejilla[s.hora_inicio + "-" + s.hora_fin] = [[], [], [], [], []];
            });

            lista.forEach(function (r) {
                var clave = r.hora_inicio + "-" + r.hora_fin;
                var dia = indiceDia(r.fecha);
                if (dia === null || !rejilla[clave]) return;
                rejilla[clave][dia].push(r);
            });

            slots.forEach(function (s) {
                var clave = s.hora_inicio + "-" + s.hora_fin;
                var fila = document.createElement("tr");

                var celdaHora = document.createElement("td");
                celdaHora.className = "celda-hora";
                celdaHora.innerHTML = hora(s.hora_inicio) + "<span>" + hora(s.hora_fin) + "</span>";
                fila.appendChild(celdaHora);

                for (var dia = 0; dia < 5; dia++) {
                    var celda = document.createElement("td");
                    celda.setAttribute("data-dia", dia);
                    if (dia === indiceHoy) celda.classList.add("hoy");

                    var enCelda = rejilla[clave][dia];
                    celda.innerHTML = enCelda.length
                        ? enCelda.map(dibujarBloque).join("")
                        : '<div class="libre"></div>';

                    fila.appendChild(celda);
                }

                cuerpo.appendChild(fila);
            });

            if (op.alPintar) op.alPintar(lista);
        }

        if (op.alAbrir) {
            cuerpo.addEventListener("click", function (e) {
                var btn = e.target.closest(".bloque");
                if (!btn) return;
                var id = btn.getAttribute("data-reserva");
                var reserva = reservas.find(function (r) { return String(r.id) === id; });
                if (reserva) op.alAbrir(reserva);
            });
        }

        pintar(reservas);

        return {
            pintar: pintar,
            filtrar: function (estado) {
                pintar(estado === "TODOS"
                    ? reservas
                    : reservas.filter(function (r) { return r.estado === estado; }));
            }
        };
    }

    /* Navegación de semanas por querystring. `inicioSemana` es el lunes que se
       está viendo; los saltos son de 7 días. */
    function navegacion(op) {
        function ir(iso) {
            var url = new URL(window.location.href);
            url.searchParams.set("week", iso);
            window.location.href = url.toString();
        }

        function desplazar(dias) {
            var base = aFecha(op.inicioSemana);
            base.setDate(base.getDate() + dias);
            ir(aIso(base));
        }

        if (op.prev) op.prev.addEventListener("click", function () { desplazar(-7); });
        if (op.next) op.next.addEventListener("click", function () { desplazar(7); });
        if (op.hoy) op.hoy.addEventListener("click", function () { ir(aIso(new Date())); });
    }

    global.RejillaSemana = {
        montar: montar,
        navegacion: navegacion,
        aFecha: aFecha,
        aIso: aIso,
        hora: hora,
        escapar: escapar,
        textoLargo: textoLargo
    };
})(window);
