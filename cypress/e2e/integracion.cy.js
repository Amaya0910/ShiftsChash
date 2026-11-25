// Pruebas de integración de ShiftCash (Apéndice B).
// Integración incremental ascendente: primero la API (rutas → servicios → BD)
// y al final el cliente React contra esa misma API.
// Ejecutar: npx cypress run --spec cypress/e2e/integracion.cy.js
const API = Cypress.env('API') || 'https://shiftschash-api.onrender.com';
const ID = Date.now(); // sufijo para no chocar con datos de ejecuciones anteriores
let token;

const auth = () => ({ Authorization: `Bearer ${token}` });
const hoy = () => new Date().toISOString().slice(0, 10);

function categoriaDeGasto() {
  return cy.request({ url: `${API}/transactions/categories`, headers: auth() })
    .its('body')
    .then((cats) => cats.find((c) => c.type !== 'income'));
}

describe('Integración ShiftCash', () => {
  before(() => {
    cy.request('POST', `${API}/auth/login`, {
      email: Cypress.env('SC_EMAIL'),
      password: Cypress.env('SC_PASS'),
    }).then((r) => { token = r.body.access_token; });
  });

  it('PI-01: rechaza una transacción sin token (401)', () => {
    cy.request({
      method: 'POST', url: `${API}/transactions/`, failOnStatusCode: false,
      body: { category_id: 1, type: 'expense', amount: 1000 },
    }).its('status').should('eq', 401);
  });

  it('PI-02: crea un gasto y aparece en el historial', () => {
    categoriaDeGasto().then((cat) => {
      cy.request({
        method: 'POST', url: `${API}/transactions/`, headers: auth(),
        body: { category_id: cat.category_id, type: 'expense', amount: 50000, description: `PI-02 ${ID}` },
      }).its('status').should('eq', 200);
      cy.request({ url: `${API}/transactions/`, headers: auth() })
        .its('body')
        .should((lista) => expect(lista.some((t) => t.description === `PI-02 ${ID}`)).to.be.true);
    });
  });

  it('PI-03: rechaza una categoría inexistente o ajena (404)', () => {
    cy.request({
      method: 'POST', url: `${API}/transactions/`, headers: auth(), failOnStatusCode: false,
      body: { category_id: 999999, type: 'expense', amount: 1000 },
    }).its('status').should('eq', 404);
  });

  it('PI-11: rechaza montos inválidos (422)', () => {
    categoriaDeGasto().then((cat) => {
      [0, -5, 1e14].forEach((amount) => {
        cy.request({
          method: 'POST', url: `${API}/transactions/`, headers: auth(), failOnStatusCode: false,
          body: { category_id: cat.category_id, type: 'expense', amount },
        }).its('status').should('eq', 422);
      });
    });
  });

  it('PI-04: un presupuesto superado refleja más del 100 % (D-04)', () => {
    const d = new Date();
    categoriaDeGasto().then((cat) => {
      cy.request({
        method: 'POST', url: `${API}/budgets/`, headers: auth(),
        body: {
          category_id: cat.category_id, name: `PI-04 ${ID}`, amount: 1,
          period_type: 'monthly', month: d.getMonth() + 1, year: d.getFullYear(),
        },
      }).then((r) => {
        expect(r.status).to.eq(201);
        cy.request({
          method: 'POST', url: `${API}/transactions/`, headers: auth(),
          body: { category_id: cat.category_id, type: 'expense', amount: 2, trans_date: hoy() },
        });
        cy.request({ url: `${API}/budgets/`, headers: auth() }).its('body').then((lista) => {
          const b = lista.find((x) => x.budget_id === r.body.budget_id);
          expect(b.percentage).to.be.gt(100);
        });
        cy.request({ method: 'DELETE', url: `${API}/budgets/${r.body.budget_id}`, headers: auth() });
      });
    });
  });

  it('PI-09: un mes fuera de 1–12 responde 422 (D-03)', () => {
    categoriaDeGasto().then((cat) => {
      cy.request({
        method: 'POST', url: `${API}/budgets/`, headers: auth(), failOnStatusCode: false,
        body: { category_id: cat.category_id, name: 'PI-09', amount: 1000, period_type: 'monthly', month: 13, year: 2026 },
      }).its('status').should('eq', 422);
    });
  });

  it('PI-06, PI-10 y PI-12: meta sin fecha final, sin cuotas negativas, y marcado de días', () => {
    cy.request({
      method: 'POST', url: `${API}/saving-goals/`, headers: auth(),
      body: { name: `PI-06 ${ID}`, target_amount: 1000 },
    }).then((r) => {
      expect(r.status).to.eq(200);
      expect(r.body.end_date).to.be.a('string');                          // D-07
      expect(Object.values(r.body.daily_amounts).every((v) => v >= 0)).to.be.true; // D-01
      const id = r.body.goal_id;
      cy.request({ method: 'POST', url: `${API}/saving-goals/${id}/toggle-day/1`, headers: auth() });
      cy.request({ method: 'POST', url: `${API}/saving-goals/${id}/toggle-day/2`, headers: auth() })
        .its('body.progress.days_completed').should('eq', 2);
      cy.request({ method: 'DELETE', url: `${API}/saving-goals/${id}`, headers: auth() });
    });
  });

  it('E2E: el cliente React inicia sesión y muestra Presupuestos', () => {
    cy.visit('/auth');
    cy.get('.form-box.login input[name=email]').type(Cypress.env('SC_EMAIL'));
    cy.get('.form-box.login input[name=password]').type(Cypress.env('SC_PASS'), { log: false });
    cy.get('.form-box.login button[type=submit]').click();
    cy.url({ timeout: 120000 }).should('include', '/dashboard');
    cy.contains('.db-nav-item', 'Presupuestos').click();
    cy.screenshot('pi-e2e-presupuestos');
  });
});
