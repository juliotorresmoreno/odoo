# -*- coding: utf-8 -*-

from odoo.addons.l10n_account_edi_ubl_cii_tests.tests.common import TestUBLCommon
from odoo.tests import tagged

@tagged('post_install_l10n', 'post_install', '-at_install')
class TestCIIFR(TestUBLCommon):

    @classmethod
    @TestUBLCommon.setup_country('fr')
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_1 = cls.env['res.partner'].create({
            'name': "partner_1",
            'street': "Rue Jean Jaurès, 42",
            'zip': "75000",
            'city': "Paris",
            'vat': 'FR05677404089',
            'country_id': cls.env.ref('base.fr').id,
            'bank_ids': [(0, 0, {'acc_number': 'FR15001559627230'})],
            'phone': '+1 (650) 555-0111',
            'email': "partner1@yourcompany.com",
            'ref': 'ref_partner_1',
            'invoice_edi_format': 'facturx',
        })

        cls.partner_2 = cls.env['res.partner'].create({
            'name': "partner_2",
            'street': "Rue Charles de Gaulle",
            'zip': "52330",
            'city': "Colombey-les-Deux-Églises",
            'vat': 'FR35562153452',
            'country_id': cls.env.ref('base.fr').id,
            'bank_ids': [(0, 0, {'acc_number': 'FR90735788866632'})],
            'ref': 'ref_partner_2',
            'invoice_edi_format': 'facturx',
        })

        cls.tax_21 = cls.env['account.tax'].create({
            'name': 'tax_21',
            'amount_type': 'percent',
            'amount': 21,
            'type_tax_use': 'sale',
            'country_id': cls.env.ref('base.fr').id,
            'sequence': 10,
        })

        cls.tax_12 = cls.env['account.tax'].create({
            'name': 'tax_12',
            'amount_type': 'percent',
            'amount': 12,
            'type_tax_use': 'sale',
            'country_id': cls.env.ref('base.fr').id,
        })

        cls.tax_21_purchase = cls.env['account.tax'].create({
            'name': 'tax_21',
            'amount_type': 'percent',
            'amount': 21,
            'type_tax_use': 'purchase',
            'country_id': cls.env.ref('base.fr').id,
        })

        cls.tax_12_purchase = cls.env['account.tax'].create({
            'name': 'tax_12',
            'amount_type': 'percent',
            'amount': 12,
            'type_tax_use': 'purchase',
            'country_id': cls.env.ref('base.fr').id,
        })

        cls.tax_5_purchase = cls.env['account.tax'].create({
            'name': 'tax_5',
            'amount_type': 'percent',
            'amount': 5,
            'type_tax_use': 'purchase',
        })

        cls.tax_0_purchase = cls.env['account.tax'].create({
            'name': 'tax_0',
            'amount_type': 'percent',
            'amount': 0,
            'type_tax_use': 'purchase',
        })

        cls.tax_5 = cls.env['account.tax'].create({
            'name': 'tax_5',
            'amount_type': 'percent',
            'amount': 5,
            'type_tax_use': 'sale',
        })

        cls.tax_5_incl = cls.env['account.tax'].create({
            'name': 'tax_5_incl',
            'amount_type': 'percent',
            'amount': 5,
            'type_tax_use': 'sale',
            'price_include_override': 'tax_included',
        })

    @classmethod
    def setup_independent_company(cls, **kwargs):
        return super().setup_independent_company(
            phone='+1 (650) 555-0111',  # [BR-DE-6] "Seller contact telephone number" (BT-42) is required
            email="info@yourcompany.com",  # [BR-DE-7] The element "Seller contact email address" (BT-43) is required
            vat='FR23334175221', # [BR-CO-26]-In order for the buyer to automatically ...
            zip='123', # [BR-DE-4] The element "Seller post code" (BT-38) must be transmitted.
            **kwargs,
        )

    ####################################################
    # Test export - import
    ####################################################

    def test_export_pdf(self):
        acc_bank = self.env['res.partner.bank'].create({
            'acc_number': 'FR15001559627231',
            'partner_id': self.company_data['company'].partner_id.id,
        })

        invoice = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_invoice',
            partner_bank_id=acc_bank.id,
            invoice_line_ids=[{
                'product_id': self.product_a.id,
                'product_uom_id': self.env.ref('uom.product_uom_dozen').id,
                'price_unit': 275.0,
                'quantity': 5,
                'discount': 20.0,
                'tax_ids': [(6, 0, self.tax_21.ids)],
            }],
        )

        pdf_attachment = invoice.ubl_cii_xml_id
        facturx_filename = self.env['account.edi.xml.cii']._export_invoice_filename(invoice)
        self.assertEqual(pdf_attachment['name'], facturx_filename)

    def test_export_import_invoice(self):
        invoice = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[
                {
                    'product_id': self.product_a.id,
                    'quantity': 2.0,
                    'product_uom_id': self.env.ref('uom.product_uom_dozen').id,
                    'price_unit': 990.0,
                    'discount': 10.0,
                    'tax_ids': [(6, 0, self.tax_21.ids)],
                },
                {
                    'product_id': self.product_b.id,
                    'quantity': 10.0,
                    'product_uom_id': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 100.0,
                    'tax_ids': [(6, 0, self.tax_12.ids)],
                },
                {
                    'product_id': self.product_b.id,
                    'quantity': -1.0,
                    'product_uom_id': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 100.0,
                    'tax_ids': [(6, 0, self.tax_12.ids)],
                },
            ],
        )
        attachment = self._assert_invoice_attachment(
            invoice.ubl_cii_xml_id,
            xpaths='''
                <xpath expr="./*[local-name()='ExchangedDocument']/*[local-name()='ID']" position="replace">
                        <ram:ID xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">___ignore___</ram:ID>
                </xpath>
                <xpath expr=".//*[local-name()='IssuerAssignedID']" position="replace">
                        <ram:IssuerAssignedID xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">___ignore___</ram:IssuerAssignedID>
                </xpath>
                <xpath expr=".//*[local-name()='PaymentReference']" position="replace">
                        <ram:PaymentReference xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">___ignore___</ram:PaymentReference>
                </xpath>
            ''',
            expected_file_path='from_odoo/facturx_out_invoice.xml',
        )
        facturx_filename = self.env['account.edi.xml.cii']._export_invoice_filename(invoice)
        self.assertEqual(attachment.name, facturx_filename)
        self._assert_imported_invoice_from_etree(invoice, attachment)

    def test_export_import_refund(self):
        refund = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_refund',
            invoice_line_ids=[
                {
                    'product_id': self.product_a.id,
                    'quantity': 2.0,
                    'product_uom_id': self.env.ref('uom.product_uom_dozen').id,
                    'price_unit': 990.0,
                    'discount': 10.0,
                    'tax_ids': [(6, 0, self.tax_21.ids)],
                },
                {
                    'product_id': self.product_b.id,
                    'quantity': 10.0,
                    'product_uom_id': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 100.0,
                    'tax_ids': [(6, 0, self.tax_12.ids)],
                },
                {
                    'product_id': self.product_b.id,
                    'quantity': -1.0,
                    'product_uom_id': self.env.ref('uom.product_uom_unit').id,
                    'price_unit': 100.0,
                    'tax_ids': [(6, 0, self.tax_12.ids)],
                },
            ],
        )
        attachment = self._assert_invoice_attachment(
            refund.ubl_cii_xml_id,
            xpaths='''
                <xpath expr="./*[local-name()='ExchangedDocument']/*[local-name()='ID']" position="replace">
                        <ram:ID xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">___ignore___</ram:ID>
                </xpath>
                <xpath expr=".//*[local-name()='IssuerAssignedID']" position="replace">
                        <ram:IssuerAssignedID xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">___ignore___</ram:IssuerAssignedID>
                </xpath>
            ''',
            expected_file_path='from_odoo/facturx_out_refund.xml'
        )
        facturx_filename = self.env['account.edi.xml.cii']._export_invoice_filename(refund)
        self.assertEqual(attachment.name, facturx_filename)
        self._assert_imported_invoice_from_etree(refund, attachment)

    def test_export_tax_included(self):
        """
        Tests whether the tax included price_units are correctly converted to tax excluded
        amounts in the exported xml
        """
        invoice = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[
                {
                    'product_id': self.product_a.id,
                    'quantity': 1,
                    'price_unit': 100,
                    'tax_ids': [(6, 0, self.tax_5_incl.ids)],
                },
                {
                    'product_id': self.product_a.id,
                    'quantity': 1,
                    'price_unit': 100,
                    'tax_ids': [(6, 0, self.tax_5.ids)],
                },
                {
                    'product_id': self.product_a.id,
                    'quantity': 1,
                    'price_unit': 200,
                    'discount': 10,
                    'tax_ids': [(6, 0, self.tax_5_incl.ids)],
                },
                {
                    'product_id': self.product_a.id,
                    'quantity': 1,
                    'price_unit': 200,
                    'discount': 10,
                    'tax_ids': [(6, 0, self.tax_5.ids)],
                },
            ],
        )
        self._assert_invoice_attachment(
            invoice.ubl_cii_xml_id,
            xpaths='''
                <xpath expr="./*[local-name()='ExchangedDocument']/*[local-name()='ID']" position="replace">
                        <ram:ID xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">___ignore___</ram:ID>
                </xpath>
                <xpath expr=".//*[local-name()='IssuerAssignedID']" position="replace">
                        <ram:IssuerAssignedID xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">___ignore___</ram:IssuerAssignedID>
                </xpath>
            ''',
            expected_file_path='from_odoo/facturx_out_invoice_tax_incl.xml'
        )

    def test_encoding_in_attachment_facturx(self):
        invoice = self._generate_move(
            seller=self.partner_1,
            buyer=self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[{'product_id': self.product_a.id}],
        )
        facturx_filename = self.env['account.edi.xml.cii']._export_invoice_filename(invoice)
        self._test_encoding_in_attachment(invoice.ubl_cii_xml_id, facturx_filename)

    def test_export_with_fixed_taxes_case1(self):
        # CASE 1: simple invoice with a recupel tax
        invoice = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[
                {
                    'product_id': self.product_a.id,
                    'quantity': 1,
                    'price_unit': 99,
                    'tax_ids': [(6, 0, [self.recupel.id, self.tax_21.id])],
                }
            ],
        )
        self.assertEqual(invoice.amount_total, 121)
        self._assert_invoice_attachment(invoice.ubl_cii_xml_id, None, 'from_odoo/facturx_ecotaxes_case1.xml')

    def test_export_with_fixed_taxes_case2(self):
        # CASE 2: Same but with several ecotaxes
        invoice = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[
                {
                    'product_id': self.product_a.id,
                    'quantity': 1,
                    'price_unit': 98,
                    'tax_ids': [(6, 0, [self.recupel.id, self.auvibel.id, self.tax_21.id])],
                }
            ],
        )
        self.assertEqual(invoice.amount_total, 121)
        self._assert_invoice_attachment(invoice.ubl_cii_xml_id, None, 'from_odoo/facturx_ecotaxes_case2.xml')

    def test_export_with_fixed_taxes_case3(self):
        # CASE 3: same as Case 1 but taxes are Price Included
        self.recupel.price_include_override = 'tax_included'
        self.tax_21.price_include_override = 'tax_included'

        # Price TTC = 121 = (99 + 1 ) * 1.21
        invoice = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[
                {
                    'product_id': self.product_a.id,
                    'quantity': 1,
                    'price_unit': 121,
                    'tax_ids': [(6, 0, [self.recupel.id, self.tax_21.id])],
                }
            ],
        )
        self.assertEqual(invoice.amount_total, 121)
        self._assert_invoice_attachment(invoice.ubl_cii_xml_id, None, 'from_odoo/facturx_ecotaxes_case3.xml')

    ####################################################
    # Test import
    ####################################################

    def test_import_partner_facturx(self):
        invoice = self._generate_move(
            seller=self.partner_1,
            buyer=self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[{'product_id': self.product_a.id}],
        )
        self._test_import_partner(invoice.ubl_cii_xml_id, self.partner_1, self.partner_2)

    def test_import_in_journal_facturx(self):
        invoice = self._generate_move(
            seller=self.partner_1,
            buyer=self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[{'product_id': self.product_a.id}],
        )
        self._test_import_in_journal(invoice.ubl_cii_xml_id)

    def test_import_and_create_partner_facturx(self):
        """ Tests whether the partner is created at import if no match is found when decoding the EDI attachment
        """
        partner_vals = {
            'name': "Buyer",
            'email': "buyer@yahoo.com",
            'phone': "1111",
            'vat': "FR89215010646",
        }
        # assert there is no matching partner
        partner_match = self.env['res.partner']._retrieve_partner(**partner_vals)
        self.assertFalse(partner_match)

        # Import attachment as an invoice
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'journal_id': self.company_data['default_journal_sale'].id,
        })
        self._update_invoice_from_file(
            module_name='l10n_account_edi_ubl_cii_tests',
            subfolder='tests/test_files/from_odoo',
            filename='facturx_test_import_partner.xml',
            invoice=invoice)

        # assert a new partner has been created
        self.assertRecordValues(invoice.partner_id, [partner_vals])

    def test_import_tax_included(self):
        """
        Tests whether the tax included / tax excluded are correctly decoded when
        importing a document. The imported xml represents the following invoice:

        Description         Quantity    Unit Price    Disc (%)   Taxes            Amount
        --------------------------------------------------------------------------------
        Product A                  1           100          0    5% (incl)         95.24
        Product A                  1           100          0    5% (not incl)       100
        Product A                  2           200         10    5% (incl)        171.43
        Product A                  2           200         10    5% (not incl)       180
        -----------------------
        Untaxed Amount: 546.67
        Taxes: 27.334
        -----------------------
        Total: 574.004
        """
        # /!\ The price_unit are different for taxes with price_include, because all amounts in Factur-X should be
        # tax excluded. At import, the tax included amounts are thus converted into tax excluded ones.
        # Yet, the line subtotals and total will be the same (if an equivalent tax exist with price_include = False)
        invoice_vals = {
            'amount_total': 574.004,
            'amount_tax': 27.334,
            'currency_id': self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id,
            'invoice_lines': [
                {'price_unit': 95.24, 'price_subtotal': 95.24, 'quantity': 1, 'discount': 0, 'tax_ids': self.tax_5_purchase.ids},
                {'price_unit': 100, 'price_subtotal': 100, 'quantity': 1, 'discount': 0, 'tax_ids': self.tax_5_purchase.ids},
                {'price_unit': 190.48, 'price_subtotal': 171.43, 'quantity': 1, 'discount': 10.001049979000411, 'tax_ids': self.tax_5_purchase.ids},
                {'price_unit': 200, 'price_subtotal': 180, 'quantity': 1, 'discount': 10.0, 'tax_ids': self.tax_5_purchase.ids},
            ]
        }
        self._assert_imported_invoice_from_file(
            subfolder='tests/test_files/from_odoo',
            filename='facturx_out_invoice_tax_incl.xml',
            # Discount of line 3: when exporting the invoice, we compute the price tax excluded = 200/1.05 ~= 190.48
            # then, when computing the discount amount: 190.48 * 0.1 ~= 19.05 => price net amount = 171.43
            # Thus, at import: price_unit = 190.48, and discount = 100 * (1 - 171.43 / 190.48) = 10.001049979
            move_type='in_invoice',
            invoice_vals=invoice_vals,
        )

    def test_import_fnfe_examples(self):
        # Source: official documentation of the FNFE (subdirectory: "5. FACTUR-X 1.0.06 - Examples")
        subfolder = 'tests/test_files/from_factur-x_doc'
        # the 2 following files have the same pdf but one is labelled as an invoice and the other as a refund
        invoice_vals = {
            'amount_total': 233.47,
            'amount_tax': 14.99,
            'invoice_lines': [{'price_subtotal': 20.48}, {'price_subtotal': 198}]
        }
        # source: Avoir_FR_type380_EN16931.pdf
        self._assert_imported_invoice_from_file(
            subfolder=subfolder,
            filename='facturx_credit_note_type380.xml',
            invoice_vals=invoice_vals,
            move_type='in_refund',
        )
        # source: Avoir_FR_type381_EN16931.pdf
        self._assert_imported_invoice_from_file(
            subfolder=subfolder,
            filename='facturx_credit_note_type381.xml',
            invoice_vals=invoice_vals,
            move_type='in_refund',
        )
        # source: Facture_F20220024_EN_16931_basis_quantity, basis quantity != 1 for one of the lines
        self._assert_imported_invoice_from_file(
            subfolder=subfolder,
            filename='facturx_invoice_basis_quantity.xml',
            invoice_vals={'amount_total': 108, 'amount_tax': 8},
        )
        # source: Facture_F20220029_EN_16931_K.pdf, credit note labelled as an invoice with negative amounts
        self._assert_imported_invoice_from_file(
            subfolder=subfolder,
            filename='facturx_invoice_negative_amounts.xml',
            invoice_vals={
                'amount_total': 100,
                'amount_tax': 0,
                'invoice_lines': [{'price_subtotal': p} for p in (-5, 10, 60, 30, 5)],
            },
            move_type='in_refund',
        )

    def test_import_fixed_taxes(self):
        """ Tests whether we correctly decode the xml attachments created using fixed taxes.
        See the tests above to create these xml attachments ('test_export_with_fixed_taxes_case_[X]').
        NB: use move_type = 'out_invoice' s.t. we can retrieve the taxes used to create the invoices.
        """
        subfolder = "tests/test_files/from_odoo"
        kwargs = {
            'subfolder': subfolder,
            'move_type': 'out_invoice',
            'invoice_vals': {
                'amount_total': 121,
                'amount_tax': 22,
                'currency_id': self.other_currency.id,
                'invoice_lines': [{
                    'name': "product_a",
                    'quantity': 1,
                    'price_unit': 99,
                    'discount': 0,
                    'tax_ids': (self.tax_21 + self.recupel).ids,
                }],
            },
        }
        self._assert_imported_invoice_from_file(filename='facturx_ecotaxes_case1.xml', **kwargs)
        self._assert_imported_invoice_from_file(filename='facturx_ecotaxes_case3.xml', **kwargs)
        kwargs['invoice_vals'].update({
            'amount_tax': 23,
            'invoice_lines': [{
                'name': "product_a",
                'quantity': 1,
                'price_unit': 98,
                'discount': 0,
                'tax_ids': (self.tax_21 + self.recupel + self.auvibel).ids,
            }],
        })
        self._assert_imported_invoice_from_file(filename='facturx_ecotaxes_case2.xml', **kwargs)

    def test_facturx_has_no_negative_lines(self):
        """
        Test that the is no negative ChargeAmount in the facturx xml
        """
        invoice = self._generate_move(
            seller=self.partner_1,
            buyer=self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[
                {'product_id': self.product_a.id, 'quantity': 1, 'price_unit': 100.0, 'tax_ids': [(6, 0, [self.tax_sale_a.id])]},
                {'product_id': self.product_b.id, 'quantity': 1, 'price_unit': -50.0, 'tax_ids': [(6, 0, [self.tax_sale_a.id])]}
            ]
        )

        self._assert_invoice_attachment(invoice.ubl_cii_xml_id, None, 'from_odoo/facturx_positive_discount_price_unit.xml')
