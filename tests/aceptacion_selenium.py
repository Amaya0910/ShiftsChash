"""Pruebas de aceptación de ShiftCash con Selenium 4 (Apéndice C).

Recorre por la interfaz desplegada los casos PA-01, PA-02, PA-03, PA-05, PA-06 y PA-08 y guarda una
captura de cada uno en docs/evidencias/. La sesión con el usuario final usa el
mismo guion de casos, pero la ejecuta esa persona y firma el acta.

Requisitos: pip install selenium  (Chrome instalado)
Variables:  SC_EMAIL, SC_PASS y, opcionales, SC_BASE_URL y SC_HEADLESS=1
Uso:        python tests/aceptacion_selenium.py
"""
import os
import pathlib
from datetime import date, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE = os.environ.get("SC_BASE_URL", "https://shifts-chash-version-amaya.vercel.app")
EVIDENCIAS = pathlib.Path(os.environ.get(
    "SC_EVIDENCIAS", pathlib.Path(__file__).resolve().parents[1] / "docs" / "evidencias"))
ESPERA_S = 120  # la API en Render puede tardar en despertar (D-09)


class ShiftCashUI:
    """Acciones de la interfaz que usan los casos de aceptación (patrón Page Object)."""

    def __init__(self, driver):
        self.d = driver
        self.w = WebDriverWait(driver, ESPERA_S)

    def abrir(self, ruta: str) -> None:
        self.d.get(f"{BASE}{ruta}")

    def iniciar_sesion(self, email: str, clave: str) -> None:
        self.abrir("/login")
        formulario = self.w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".form-box.login form")))
        formulario.find_element(By.NAME, "email").send_keys(email)
        formulario.find_element(By.NAME, "password").send_keys(clave)
        formulario.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        self.w.until(EC.url_contains("/dashboard"))

    def abrir_modal_transaccion(self) -> None:
        self.w.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Transacción')]"))).click()
        self.w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-card")))

    def elegir_primera_categoria(self) -> str:
        self.d.find_element(By.CSS_SELECTOR, ".modal-card .custom-select-trigger").click()
        opcion = self.w.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".modal-card .custom-select-option:not(.disabled)")))
        nombre = opcion.text
        opcion.click()
        return nombre

    def llenar_transaccion(self, monto: str, descripcion: str) -> None:
        self.d.find_element(By.NAME, "amount").send_keys(monto)
        self.d.find_element(By.NAME, "description").send_keys(descripcion)

    def enviar_modal(self) -> None:
        self.d.find_element(By.CSS_SELECTOR, "button.modal-submit").click()

    def fijar_fecha(self, selector: str, iso: str) -> None:
        """Escribe una fecha AAAA-MM-DD en un <input type=date> controlado por React."""
        campo = self.d.find_element(By.CSS_SELECTOR, selector)
        self.d.execute_script(
            "const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;"
            "set.call(arguments[0], arguments[1]);"
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", campo, iso)

    def ir_a(self, vista: str) -> None:
        self.w.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class,'db-nav-item')][contains(., '{vista}')]"))).click()

    def captura(self, nombre: str) -> None:
        EVIDENCIAS.mkdir(parents=True, exist_ok=True)
        self.d.save_screenshot(str(EVIDENCIAS / f"{nombre}.png"))


def pa01_ruta_privada_sin_sesion(ui: ShiftCashUI) -> None:
    ui.abrir("/dashboard")
    ui.w.until(EC.url_contains("/login"))
    ui.captura("pa01_redirige_login")


def pa02_registrar_gasto(ui: ShiftCashUI, descripcion: str) -> None:
    ui.abrir_modal_transaccion()
    ui.llenar_transaccion("45000", descripcion)
    ui.elegir_primera_categoria()
    ui.captura("pa02_formulario")
    ui.enviar_modal()
    ui.w.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-card")))
    ui.ir_a("Historial")
    ui.w.until(EC.visibility_of_element_located(
        (By.XPATH, f"//div[contains(@class,'hist-fila')][contains(., '{descripcion}')]")))
    ui.captura("pa02_historial")


def pa03_ingreso_recurrente(ui: ShiftCashUI, descripcion: str) -> None:
    ui.abrir_modal_transaccion()
    ui.d.find_element(By.XPATH, "//div[contains(@class,'modal-card')]//button[contains(., 'Ingreso')]").click()
    ui.llenar_transaccion("2500000", descripcion)
    ui.elegir_primera_categoria()
    ui.d.find_element(By.CSS_SELECTOR, ".modal-card .modal-recurrente-toggle").click()
    Select(ui.w.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".modal-card select[name=frequency]")))).select_by_value("monthly")
    ui.captura("pa03_formulario")
    ui.enviar_modal()
    ui.w.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-card")))
    ui.ir_a("Historial")
    fila = ui.w.until(EC.visibility_of_element_located(
        (By.XPATH, f"//div[contains(@class,'hist-fila')][contains(., '{descripcion}')]")))
    assert fila.find_elements(By.CSS_SELECTOR, ".hist-recurrente-badge"), "debe mostrarse como recurrente"
    ui.captura("pa03_historial")


def pa05_crear_presupuesto(ui: ShiftCashUI, nombre: str) -> None:
    ui.ir_a("Presupuestos")
    ui.w.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Nuevo Presupuesto')]"))).click()
    modal = ui.w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".presupuestos-modal")))
    modal.find_element(By.CSS_SELECTOR, ".custom-select-trigger").click()
    ui.w.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".presupuestos-modal .custom-select-option:not(.disabled)"))).click()
    modal.find_element(By.NAME, "name").send_keys(nombre)
    modal.find_element(By.NAME, "amount").send_keys("600000")
    ui.captura("pa05_formulario")
    modal.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    ui.w.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".presupuestos-modal")))
    ui.w.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{nombre}')]")))
    ui.captura("pa05_tarjeta")


def pa06_presupuesto_superado(ui: ShiftCashUI) -> None:
    """Deja evidencia de la vista Presupuestos; el porcentaje real se revisa en la captura."""
    ui.ir_a("Presupuestos")
    ui.w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".presupuestos-card-category")))
    ui.captura("pa06_presupuestos")


def pa08_meta_monto_no_redondo(ui: ShiftCashUI) -> None:
    ui.ir_a("Metas de Ahorro")
    ui.w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-nueva-meta, .btn-crear-primera-meta"))).click()
    ui.w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-card input[name=name]"))).send_keys("Meta PA-08")
    ui.d.find_element(By.CSS_SELECTOR, ".modal-card input[name=target_amount]").send_keys("1500")
    fin = (date.today() + timedelta(days=30)).isoformat()
    ui.fijar_fecha(".modal-card input[name=end_date]", fin)
    ui.d.find_element(By.CSS_SELECTOR, ".modal-card button[type=submit]").click()
    mensaje = ui.w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-error")))
    assert "1000" in mensaje.text, f"Mensaje inesperado: {mensaje.text}"
    ui.captura("pa08_validacion_meta")


def crear_driver():
    opciones = webdriver.ChromeOptions()
    if os.environ.get("SC_HEADLESS"):
        opciones.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opciones)
    driver.set_window_size(1366, 900)
    return driver


def main() -> None:
    driver = crear_driver()
    ui = ShiftCashUI(driver)
    try:
        pa01_ruta_privada_sin_sesion(ui)
        print("PA-01 OK")
        ui.iniciar_sesion(os.environ["SC_EMAIL"], os.environ["SC_PASS"])
        pa02_registrar_gasto(ui, "Almuerzo PA-02")
        print("PA-02 OK")
        pa03_ingreso_recurrente(ui, "Salario PA-03")
        print("PA-03 OK")
        pa05_crear_presupuesto(ui, "Presupuesto PA-05")
        print("PA-05 OK")
        pa06_presupuesto_superado(ui)
        print("PA-06 captura guardada")
        pa08_meta_monto_no_redondo(ui)
        print("PA-08 OK")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
