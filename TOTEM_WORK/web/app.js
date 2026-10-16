// La web usa la API compartida con el Tótem Kivy. Ajusta esta dirección si la API está en otro equipo.
const API_BASE = (window.TOTEM_API_BASE || "http://127.0.0.1:8001").replace(/\/$/, "");
const viewIds = ["homeView","catalogView","detailView","ticketView","bookingView","bookingTicketView","statusView"];
let tramites = [], selected = null, lastTicket = "", lastReservation = "";
// Catálogo web sincronizado con client/screens/tramites.py (CATEGORIES de Kivy).
const KIVY_CATALOG = [
  {codigo:"SAP", nombre:"Subsidio de Agua Potable", departamento:"Beneficios sociales", descripcion:"Cédula de identidad, antecedente del Registro Social de Hogares y cuenta de agua."},
  {codigo:"EDA", nombre:"Exención de Derechos de Aseo", departamento:"Beneficios sociales", descripcion:"Cédula de identidad, rol o dirección del domicilio y antecedentes de respaldo."},
  {codigo:"SUF", nombre:"Subsidio Único Familiar", departamento:"Beneficios sociales", descripcion:"Cédula de identidad y certificados de nacimiento o antecedentes de causantes, según corresponda."},
  {codigo:"POD", nombre:"Solicitud de poda", departamento:"Solicitudes municipales", descripcion:"Indique dirección, referencia, descripción y fotografía si está disponible."},
  {codigo:"LUM", nombre:"Solicitud de mantención de luminaria", departamento:"Solicitudes municipales", descripcion:"Indique dirección, referencia, descripción, fotografía y si está en vía pública o área verde."},
  {codigo:"VOL", nombre:"Retiro de voluminosos", departamento:"Solicitudes municipales", descripcion:"Indique dirección, referencia y descripción del residuo voluminoso."},
  {codigo:"DEM", nombre:"Solicitud de demarcación", departamento:"Solicitudes municipales", descripcion:"Permite solicitar evaluación de demarcación vial o peatonal."},
  {codigo:"DEN", nombre:"Denuncias y fiscalización", departamento:"Denuncias y fiscalización", descripcion:"Motivos disponibles: retiro de rucos, retiro de autos, insalubridad, negocio irregular u otro. No se solicitan datos personales."}
];
const KIVY_BOOKINGS = [
  "Agenda para el Registro Social de Hogares",
  "Atención Clínica Veterinaria",
  "Esterilización Canina",
  "Esterilización Felina"
];
const $ = id => document.getElementById(id);
function showView(id){viewIds.forEach(v=>$(v).classList.toggle("hidden",v!==id));window.scrollTo({top:0,behavior:"smooth"});}
document.querySelectorAll("[data-show]").forEach(b=>b.addEventListener("click",()=>showView(b.dataset.show)));
document.querySelectorAll("[data-action='catalog']").forEach(b=>b.addEventListener("click",()=>{showView("catalogView");loadTramites();}));
$("startBtn").addEventListener("click",()=>{showView("catalogView");loadTramites();});
$("reloadBtn").addEventListener("click",loadTramites);
$("searchInput").addEventListener("input",renderTramites);
function safeText(v){return String(v??"");}
async function api(path, options={}){
  const response=await fetch(`${API_BASE}${path}`,options); let body={};
  const raw=await response.text(); try{body=raw?JSON.parse(raw):{};}catch{body={detail:raw};}
  if(!response.ok){const detail=body.detail;throw new Error(typeof detail==="string"?detail:(detail?JSON.stringify(detail):`Error HTTP ${response.status}`));}
  return body;
}
async function checkApi(){const badge=$("apiStatus");try{await api("/health");badge.className="status online";badge.querySelector("span").textContent="API conectada";}catch{badge.className="status offline";badge.querySelector("span").textContent="API desconectada";}}
function getName(t){return t.nombre||t.nombre_tramite||t.tramite||t.descripcion||`Trámite ${t.id??""}`.trim();}
function getCode(t){return t.codigo||t.codigo_tramite||t.codigo_tramite_municipal||t.id||"";}
async function loadTramites(){
  const list=$("tramitesList"),msg=$("catalogMessage");
  list.innerHTML='<div class="loading">Consultando el servidor municipal…</div>';msg.textContent="";
  try{
    const data=await api("/tramites");
    const apiItems=Array.isArray(data)?data:(data.tramites||data.items||[]);
    const activeByCode=new Map(apiItems.map(t=>[String(getCode(t)).toUpperCase(),t]));
    // Solo mostrar los trámites que también aparecen en las categorías del Tótem Kivy.
    tramites=KIVY_CATALOG.filter(t=>activeByCode.has(t.codigo)).map(t=>({...t,...activeByCode.get(t.codigo),codigo:t.codigo,nombre:t.nombre,departamento:t.departamento,descripcion:t.descripcion}));
    if(!tramites.length){list.innerHTML='<div class="empty">La API está activa, pero no hay trámites de las categorías Kivy habilitados en el catálogo del servidor.</div>';msg.textContent="Revisa que SAP, EDA, SUF, POD, LUM, VOL, DEM y DEN estén activos en PostgreSQL.";return;}
    renderTramites();
  }catch(e){list.innerHTML='<div class="empty">No fue posible cargar los trámites.</div>';msg.textContent=`${e.message}. Comprueba que FastAPI esté activo y que CORS permita esta dirección web.`;}
}
function renderTramites(){
  const list=$("tramitesList"),q=$("searchInput").value.toLowerCase().trim();
  const filtered=tramites.filter(t=>`${getName(t)} ${getCode(t)} ${t.departamento}`.toLowerCase().includes(q));
  if(!filtered.length){list.innerHTML='<div class="empty">No hay coincidencias con la búsqueda.</div>';return;}
  list.replaceChildren();
  const groups=["Beneficios sociales","Solicitudes municipales","Denuncias y fiscalización"];
  groups.forEach(group=>{
    const items=filtered.filter(t=>t.departamento===group);if(!items.length)return;
    const heading=document.createElement("h2");heading.className="catalog-group-title";heading.textContent=group;list.append(heading);
    items.forEach(t=>{const b=document.createElement("button");b.className="tramite-card";const tag=document.createElement("span");tag.className="tag";tag.textContent=t.departamento;const name=document.createElement("strong");name.textContent=getName(t);const desc=document.createElement("span");desc.className="message";desc.textContent=t.descripcion;const code=document.createElement("span");code.className="card-code";code.textContent=`Código: ${getCode(t)}`;b.append(tag,name,desc,code);b.addEventListener("click",()=>selectTramite(t));list.append(b);});
  });
}
function selectTramite(t){selected=t;$("selectedName").textContent=getName(t);$("selectedDescription").textContent=t.descripcion||"Completa los datos para registrar la solicitud.";$("requestError").textContent="";$("requestForm").reset();showView("detailView");}
function normRut(s){return s.trim().toUpperCase().replace(/\./g,"").replace(/\s/g,"");}
$("rut").addEventListener("blur",e=>{const v=normRut(e.target.value);if(v.length>1)e.target.value=v.slice(0,-1)+"-"+v.slice(-1);});
$("bookingRut").addEventListener("blur",e=>{const v=normRut(e.target.value);if(v.length>1)e.target.value=v.slice(0,-1)+"-"+v.slice(-1);});
$("requestForm").addEventListener("submit",async e=>{e.preventDefault();if(!selected)return;const btn=$("submitRequest"),err=$("requestError");err.textContent="";btn.disabled=true;btn.textContent="Enviando solicitud…";const codigo=getCode(selected);const fields={nombre:$("fullName").value.trim(),rut:normRut($("rut").value),contacto:$("contact").value.trim(),direccion:$("address").value.trim(),descripcion:$("requestDescription").value.trim()};try{const data=await api("/solicitudes/publica",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({codigo_tramite:codigo, ...fields})});lastTicket=data.codigo_solicitud||data.codigo||"";if(!lastTicket)throw new Error("El servidor no devolvió el código de ticket.");$("ticketCode").textContent=lastTicket;$("ticketName").textContent=getName(selected);$("statusCode").value=lastTicket;showView("ticketView");}catch(error){err.textContent=`No se pudo registrar: ${error.message}. Este trámite podría requerir autenticación o no estar habilitado para ingreso público.`;}finally{btn.disabled=false;btn.textContent="Enviar solicitud y generar ticket →";}});
$("copyTicket").addEventListener("click",()=>copyCode(lastTicket));
function copyCode(code){if(!code)return; if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(code).then(()=>alert("Código copiado.")).catch(()=>prompt("Copia el código:",code));else prompt("Copia el código:",code);}
const today=new Date();$("bookingDate").min=`${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()).padStart(2,"0")}`;
$("service").addEventListener("change",loadSlots);$("bookingDate").addEventListener("change",loadSlots);
async function loadSlots(){const service=$("service").value,fecha=$("bookingDate").value,select=$("bookingTime"),msg=$("bookingMessage");select.innerHTML='<option value="">Consultando horarios…</option>';select.disabled=true;msg.textContent="";if(!service||!fecha){select.innerHTML='<option value="">Primero elige servicio y fecha</option>';return;}try{const data=await api(`/reservas/disponibilidad?servicio=${encodeURIComponent(service)}&fecha=${encodeURIComponent(fecha)}`);const slots=Array.isArray(data.horarios)?data.horarios:[];select.replaceChildren();const available=slots.filter(s=>s.disponible);if(!available.length){select.add(new Option("No hay horarios disponibles",""));msg.textContent="No hay horarios disponibles para esa fecha. Prueba otro día.";return;}select.add(new Option("Selecciona una hora",""));available.forEach(s=>select.add(new Option(s.hora,s.hora)));select.disabled=false;msg.textContent=`${available.length} horarios disponibles.`;}catch(e){select.innerHTML='<option value="">No se pudieron cargar horarios</option>';msg.textContent=e.message;}}
$("bookingForm").addEventListener("submit",async e=>{e.preventDefault();const btn=$("submitBooking"),err=$("bookingError");err.textContent="";btn.disabled=true;btn.textContent="Confirmando reserva…";try{const data=await api("/reservas",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({servicio:$("service").value,fecha:$("bookingDate").value,hora:$("bookingTime").value,nombre:$("bookingName").value.trim(),rut:normRut($("bookingRut").value),contacto:$("bookingContact").value.trim()})});lastReservation=data.codigo_reserva||"";$("reservationCode").textContent=lastReservation;$("reservationDetails").textContent=`${data.servicio} · ${data.fecha} · ${data.hora}`;$("bookingForm").reset();$("bookingTime").disabled=true;showView("bookingTicketView");}catch(error){err.textContent=`No se pudo confirmar la reserva: ${error.message}`;await loadSlots();}finally{btn.disabled=false;btn.textContent="Confirmar reserva →";}});
$("copyReservation").addEventListener("click",()=>copyCode(lastReservation));
$("statusForm").addEventListener("submit",async e=>{e.preventDefault();const err=$("statusError"),result=$("statusResult");err.textContent="";result.classList.add("hidden");try{const code=encodeURIComponent($("statusCode").value.trim().toUpperCase());const data=await api(`/publico/solicitudes/${code}`);result.replaceChildren();[["Ticket",data.codigo_solicitud],["Trámite",data.nombre_tramite],["Estado",data.estado],["Fecha de ingreso",data.fecha_solicitud?new Date(data.fecha_solicitud).toLocaleString("es-CL"):"No informada"]].forEach(([label,value])=>{const row=document.createElement("div");row.className="result-row";const l=document.createElement("span");l.textContent=label;const v=document.createElement(label==="Estado"?"strong":"span");v.textContent=value||"No informado";if(label==="Estado")v.className="state-pill";row.append(l,v);result.append(row);});result.classList.remove("hidden");}catch(error){err.textContent=`No se pudo consultar el ticket: ${error.message}`;}});
checkApi();setInterval(checkApi,20000);