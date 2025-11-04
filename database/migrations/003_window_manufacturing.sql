-- ============================================
-- Window Manufacturing System - Database Schema
-- Phase 3: Create all tables with RLS policies
-- ============================================

-- ============================================
-- Table 1: window_orders
-- ============================================

CREATE TABLE IF NOT EXISTS window_orders (
    id SERIAL PRIMARY KEY,
    po_number TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_id INTEGER REFERENCES po_clients(id) ON DELETE SET NULL,
    order_date TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_production', 'printed', 'completed')),
    notes TEXT,
    total_windows INTEGER DEFAULT 0,

    -- Standard company-scoped audit trail
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),
    deleted_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,

    -- Unique constraint: po_number per company
    CONSTRAINT unique_po_per_company UNIQUE (company_id, po_number)
);

-- Indexes for window_orders
CREATE INDEX IF NOT EXISTS idx_window_orders_company_id ON window_orders(company_id);
CREATE INDEX IF NOT EXISTS idx_window_orders_po_number ON window_orders(po_number);
CREATE INDEX IF NOT EXISTS idx_window_orders_customer_id ON window_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_window_orders_status ON window_orders(status);
CREATE INDEX IF NOT EXISTS idx_window_orders_order_date ON window_orders(order_date DESC);

-- RLS for window_orders
ALTER TABLE window_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their company's window orders"
    ON window_orders FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
        AND deleted_at IS NULL
    );

CREATE POLICY "Users can insert window orders for their company"
    ON window_orders FOR INSERT
    WITH CHECK (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can update their company's window orders"
    ON window_orders FOR UPDATE
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
        AND deleted_at IS NULL
    );

CREATE POLICY "Users can soft delete their company's window orders"
    ON window_orders FOR DELETE
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

-- ============================================
-- Table 2: window_order_items
-- ============================================

CREATE TABLE IF NOT EXISTS window_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES window_orders(id) ON DELETE CASCADE,
    window_type TEXT NOT NULL,
    thickness NUMERIC(10, 4) NOT NULL,  -- Store as decimal, e.g., 1.5 for 1 1/2"
    width NUMERIC(10, 4) NOT NULL,
    height NUMERIC(10, 4) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    shape_notes TEXT,

    -- Standard company-scoped audit trail
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),
    deleted_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes for window_order_items
CREATE INDEX IF NOT EXISTS idx_window_order_items_company_id ON window_order_items(company_id);
CREATE INDEX IF NOT EXISTS idx_window_order_items_order_id ON window_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_window_order_items_window_type ON window_order_items(window_type);

-- RLS for window_order_items
ALTER TABLE window_order_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their company's window order items"
    ON window_order_items FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
        AND deleted_at IS NULL
    );

CREATE POLICY "Users can insert window order items for their company"
    ON window_order_items FOR INSERT
    WITH CHECK (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can update their company's window order items"
    ON window_order_items FOR UPDATE
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
        AND deleted_at IS NULL
    );

CREATE POLICY "Users can soft delete their company's window order items"
    ON window_order_items FOR DELETE
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

-- ============================================
-- Table 3: window_labels
-- ============================================

CREATE TABLE IF NOT EXISTS window_labels (
    id SERIAL PRIMARY KEY,
    order_item_id INTEGER NOT NULL REFERENCES window_order_items(id) ON DELETE CASCADE,
    label_number INTEGER NOT NULL CHECK (label_number > 0),  -- 1 of 4, 2 of 4, etc.
    zpl_code TEXT,  -- Generated ZPL for reprinting
    print_status TEXT DEFAULT 'pending' CHECK (print_status IN ('pending', 'printed', 'reprinted')),
    printed_at TIMESTAMP,
    printed_by UUID REFERENCES auth.users(id),

    -- Standard company-scoped audit trail
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),

    -- Each label number should be unique per order item
    CONSTRAINT unique_label_per_item UNIQUE (order_item_id, label_number)
);

-- Indexes for window_labels
CREATE INDEX IF NOT EXISTS idx_window_labels_company_id ON window_labels(company_id);
CREATE INDEX IF NOT EXISTS idx_window_labels_order_item_id ON window_labels(order_item_id);
CREATE INDEX IF NOT EXISTS idx_window_labels_print_status ON window_labels(print_status);
CREATE INDEX IF NOT EXISTS idx_window_labels_printed_by ON window_labels(printed_by);

-- RLS for window_labels
ALTER TABLE window_labels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their company's window labels"
    ON window_labels FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can insert window labels for their company"
    ON window_labels FOR INSERT
    WITH CHECK (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can update their company's window labels"
    ON window_labels FOR UPDATE
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

-- ============================================
-- Table 4: label_printer_config
-- ============================================

CREATE TABLE IF NOT EXISTS label_printer_config (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    ip_address TEXT,
    port INTEGER DEFAULT 9100,
    label_width NUMERIC(5, 2) DEFAULT 3.0,   -- Default 3 inches
    label_height NUMERIC(5, 2) DEFAULT 2.0,  -- Default 2 inches
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,

    -- Standard company-scoped audit trail
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for label_printer_config
CREATE INDEX IF NOT EXISTS idx_label_printer_config_company_id ON label_printer_config(company_id);
CREATE INDEX IF NOT EXISTS idx_label_printer_config_is_default ON label_printer_config(is_default);

-- RLS for label_printer_config
ALTER TABLE label_printer_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their company's printer configs"
    ON label_printer_config FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Admins can insert printer configs for their company"
    ON label_printer_config FOR INSERT
    WITH CHECK (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Admins can update their company's printer configs"
    ON label_printer_config FOR UPDATE
    USING (
        company_id IN (
            SELECT company_id FROM user_profiles WHERE id = auth.uid()
        )
    );

-- ============================================
-- Trigger Functions for Audit Trail
-- ============================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_window_orders_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.updated_by = auth.uid();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER window_orders_update_timestamp
    BEFORE UPDATE ON window_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_window_orders_updated_at();

CREATE TRIGGER window_order_items_update_timestamp
    BEFORE UPDATE ON window_order_items
    FOR EACH ROW
    EXECUTE FUNCTION update_window_orders_updated_at();

CREATE TRIGGER label_printer_config_update_timestamp
    BEFORE UPDATE ON label_printer_config
    FOR EACH ROW
    EXECUTE FUNCTION update_window_orders_updated_at();

-- ============================================
-- Trigger to auto-calculate total_windows
-- ============================================

CREATE OR REPLACE FUNCTION calculate_total_windows()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalculate total_windows for the affected order
    UPDATE window_orders
    SET total_windows = (
        SELECT COALESCE(SUM(quantity), 0)
        FROM window_order_items
        WHERE order_id = COALESCE(NEW.order_id, OLD.order_id)
        AND deleted_at IS NULL
    )
    WHERE id = COALESCE(NEW.order_id, OLD.order_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER update_total_windows_on_insert
    AFTER INSERT ON window_order_items
    FOR EACH ROW
    EXECUTE FUNCTION calculate_total_windows();

CREATE TRIGGER update_total_windows_on_update
    AFTER UPDATE ON window_order_items
    FOR EACH ROW
    EXECUTE FUNCTION calculate_total_windows();

CREATE TRIGGER update_total_windows_on_delete
    AFTER DELETE ON window_order_items
    FOR EACH ROW
    EXECUTE FUNCTION calculate_total_windows();

-- ============================================
-- Helper Function: Auto-generate labels
-- ============================================

CREATE OR REPLACE FUNCTION generate_labels_for_order_item(
    p_order_item_id INTEGER,
    p_company_id UUID,
    p_created_by UUID
)
RETURNS INTEGER AS $$
DECLARE
    v_quantity INTEGER;
    v_label_count INTEGER;
    i INTEGER;
BEGIN
    -- Get the quantity for this order item
    SELECT quantity INTO v_quantity
    FROM window_order_items
    WHERE id = p_order_item_id;

    IF v_quantity IS NULL THEN
        RAISE EXCEPTION 'Order item % not found', p_order_item_id;
    END IF;

    -- Generate labels
    v_label_count := 0;
    FOR i IN 1..v_quantity LOOP
        INSERT INTO window_labels (
            order_item_id,
            label_number,
            company_id,
            created_by
        ) VALUES (
            p_order_item_id,
            i,
            p_company_id,
            p_created_by
        );
        v_label_count := v_label_count + 1;
    END LOOP;

    RETURN v_label_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- Verification and Summary
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================';
    RAISE NOTICE '✓ Window Manufacturing Schema Created';
    RAISE NOTICE '============================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Tables Created:';
    RAISE NOTICE '  1. window_orders';
    RAISE NOTICE '  2. window_order_items';
    RAISE NOTICE '  3. window_labels';
    RAISE NOTICE '  4. label_printer_config';
    RAISE NOTICE '';
    RAISE NOTICE 'Features Enabled:';
    RAISE NOTICE '  ✓ Row Level Security (RLS)';
    RAISE NOTICE '  ✓ Company scoping';
    RAISE NOTICE '  ✓ Soft delete support';
    RAISE NOTICE '  ✓ Audit trails';
    RAISE NOTICE '  ✓ Auto-calculate total_windows';
    RAISE NOTICE '  ✓ Label generation helper function';
    RAISE NOTICE '';
    RAISE NOTICE 'Ready for seed data!';
    RAISE NOTICE '============================================';
END $$;
