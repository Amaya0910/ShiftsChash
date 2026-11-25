-- D-05: transactions.category_id es NOT NULL, así que al borrar una categoría
-- no se puede poner en NULL. La regla correcta es impedir el borrado (RESTRICT);
-- la API ya responde 409 antes de llegar a la base de datos.
-- Aplicar una vez en la base de producción (Supabase > SQL Editor).
-- Base.metadata.create_all no modifica tablas que ya existen.

BEGIN;

ALTER TABLE transactions
    DROP CONSTRAINT IF EXISTS transactions_category_id_fkey;

ALTER TABLE transactions
    ADD CONSTRAINT transactions_category_id_fkey
    FOREIGN KEY (category_id) REFERENCES category (category_id) ON DELETE RESTRICT;

COMMIT;

-- Verificación: debe mostrar "r" (RESTRICT) en confdeltype
-- SELECT conname, confdeltype FROM pg_constraint WHERE conname = 'transactions_category_id_fkey';
