# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestStockPickingProductAvailabilityInline(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Availability Inline",
                "default_code": "TEST",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.warehouse1 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse 1", "code": "AI1"}
        )
        cls.warehouse2 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse 2", "code": "AI2"}
        )
        StockQuant = cls.env["stock.quant"]
        StockQuant.create(
            {
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "location_id": cls.warehouse1.lot_stock_id.id,
                "quantity": 10.00,
            }
        )
        StockQuant.create(
            {
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "location_id": cls.warehouse2.lot_stock_id.id,
                "quantity": 20.00,
            }
        )

    def test_stock_picking_product_rec_name(self):
        self.env.ref("product.decimal_product_uom").write({"digits": 3})
        # Show free_qty in warehouse1
        self.assertEqual(
            self.product.with_context(warehouse_id=self.warehouse1.id).free_qty,
            10.0,
        )
        name_search = (
            self.env["product.product"]
            .with_context(warehouse_id=self.warehouse1.id, sp_product_stock_inline=True)
            .name_search(name=self.product.display_name)
        )
        self.assertTrue(name_search[0][1].endswith("(10.000 Units)"))
        # Show free_qty in warehouse2
        self.assertEqual(
            self.product.with_context(warehouse_id=self.warehouse2.id).free_qty,
            20.0,
        )
        name_search = (
            self.env["product.product"]
            .with_context(warehouse_id=self.warehouse2.id, sp_product_stock_inline=True)
            .name_search(name=self.product.display_name)
        )
        self.assertTrue(name_search[0][1].endswith("(20.000 Units)"))
