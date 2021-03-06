# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cb_test.tests.test_cb import TestCB
from odoo.exceptions import ValidationError
from odoo.tests.common import at_install, post_install


@post_install(True)
@at_install(False)
class TestCBLaboratory(TestCB):
    def setUp(self):
        super().setUp()
        self.coverage_template.laboratory_code = "1"
        self.coverage_template_2.laboratory_code = "2"
        self.lab_service = self.env["medical.laboratory.service"].create(
            {
                "code": "INTERNAL_CODE",
                "laboratory_code": "LAB_CODE",
                "service_price_ids": [
                    (0, 0, {"laboratory_code": "1", "amount": 10, "cost": 5})
                ],
            }
        )
        self.lab_service_2 = self.env["medical.laboratory.service"].create(
            {
                "code": "INTERNAL_CODE2",
                "laboratory_code": "LAB_CODE2",
                "service_price_ids": [
                    (0, 0, {"laboratory_code": "1", "amount": 10, "cost": 5})
                ],
            }
        )
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        self.action4 = self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.lab_activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "laboratory_service_ids": [(4, self.lab_service.id)],
                "is_billable": False,
                "name": "Action4",
            }
        )
        self.enc, self.careplan, self.group = self.create_careplan_and_group(
            self.agreement_line
        )

    def test_laboratory_onchange_error(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        event = lab_req.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": self.lab_service.laboratory_code,
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        event.laboratory_service_id = self.lab_service
        event._onchange_laboratory_service()
        self.assertFalse(event.is_sellable_private)
        self.assertFalse(event.is_sellable_insurance)
        self.assertEqual(
            event.laboratory_code, self.lab_service.laboratory_code
        )
        event.write(
            {
                "laboratory_service_id": self.lab_service_2.id,
                "laboratory_code": self.lab_service_2.laboratory_code,
            }
        )
        with self.assertRaises(ValidationError):
            event._onchange_laboratory_service()

    def test_laboratory_onchange_100_0(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        event = lab_req.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": "TEST",
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_05.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 0.0,
                "coverage_percentage": 100.0,
                "authorization_method_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        event.write(
            {
                "laboratory_service_id": self.lab_service_2.id,
                "laboratory_code": self.lab_service_2.laboratory_code,
            }
        )
        event._onchange_laboratory_service()
        self.assertFalse(event.is_sellable_private)
        self.assertTrue(event.is_sellable_insurance)
        self.assertEqual(event.coverage_amount, 10)
        self.assertEqual(event.private_amount, 0)
        self.assertEqual(event.coverage_cost, 5)
        self.assertEqual(event.private_cost, 0)

    def test_laboratory_onchange_50_50(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        event = lab_req.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": "TEST",
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_05.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 0.0,
                "coverage_percentage": 50.0,
                "authorization_method_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        event.write(
            {
                "laboratory_service_id": self.lab_service_2.id,
                "laboratory_code": self.lab_service_2.laboratory_code,
            }
        )
        event._onchange_laboratory_service()
        self.assertTrue(event.is_sellable_private)
        self.assertTrue(event.is_sellable_insurance)
        self.assertEqual(event.coverage_amount, 5)
        self.assertEqual(event.private_amount, 5)
        self.assertEqual(event.coverage_cost, 2.5)
        self.assertEqual(event.private_cost, 2.5)

    def test_laboratory_onchange_0_100(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        event = lab_req.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": "TEST",
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        self.env["medical.coverage.agreement.item"].create(
            {
                "product_id": self.product_05.id,
                "coverage_agreement_id": self.agreement.id,
                "total_price": 0.0,
                "coverage_percentage": 0.0,
                "authorization_method_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "cb_medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        event.write(
            {
                "laboratory_service_id": self.lab_service_2.id,
                "laboratory_code": self.lab_service_2.laboratory_code,
            }
        )
        event._onchange_laboratory_service()
        self.assertTrue(event.is_sellable_private)
        self.assertFalse(event.is_sellable_insurance)
        self.assertEqual(event.coverage_amount, 0)
        self.assertEqual(event.private_amount, 10)
        self.assertEqual(event.coverage_cost, 0)
        self.assertEqual(event.private_cost, 5)

    def test_laboratory_constrains(self):
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        self.assertTrue(lab_req)
        event = lab_req.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": self.lab_service.laboratory_code + "111",
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        with self.assertRaises(ValidationError):
            event.laboratory_service_id = self.lab_service

    def test_laboratory(self):
        self.assertTrue(self.group.laboratory_request_ids)
        action = self.group.with_context(
            model_name="medical.laboratory.request"
        ).action_view_request()
        self.assertEqual(
            self.group.laboratory_request_ids,
            self.env["medical.laboratory.request"].search(action["domain"]),
        )
        with self.assertRaises(ValidationError):
            self.env["wizard.medical.encounter.close"].create(
                {
                    "encounter_id": self.enc.id,
                    "pos_session_id": self.session.id,
                }
            ).run()
        for lab_req in self.group.laboratory_request_ids:
            self.assertEqual(lab_req.laboratory_event_count, 0)
            event = lab_req.generate_event(
                {
                    "is_sellable_insurance": True,
                    "is_sellable_private": True,
                    "private_amount": 20,
                    "performer_id": self.practitioner_01.id,
                    "coverage_amount": 10,
                    "private_cost": 18,
                    "coverage_cost": 9,
                    "laboratory_code": "1234",
                }
            )
            self.assertEqual(
                event.id, lab_req.action_view_laboratory_events()["res_id"]
            )
            self.assertEqual(lab_req.laboratory_event_count, 1)
            lab_req.generate_event(
                {
                    "is_sellable_insurance": False,
                    "is_sellable_private": False,
                    "private_amount": 20,
                    "laboratory_code": "12345",
                    "performer_id": self.practitioner_01.id,
                    "coverage_amount": 10,
                    "private_cost": 18,
                    "coverage_cost": 9,
                }
            )
            self.assertEqual(lab_req.laboratory_event_count, 2)
        lab_req = self.group.laboratory_request_ids.filtered(
            lambda r: self.lab_service in r.laboratory_service_ids
        )
        self.assertTrue(lab_req)
        event = lab_req.generate_event(
            {
                "is_sellable_insurance": False,
                "is_sellable_private": False,
                "private_amount": 20,
                "laboratory_code": self.lab_service.laboratory_code,
                "performer_id": self.practitioner_01.id,
                "coverage_amount": 10,
                "private_cost": 18,
                "coverage_cost": 9,
            }
        )
        event.laboratory_service_id = self.lab_service
        event._onchange_laboratory_service()
        self.assertFalse(event.is_sellable_private)
        self.assertFalse(event.is_sellable_insurance)
        self.assertEqual(
            event.laboratory_code, self.lab_service.laboratory_code
        )
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": self.enc.id, "pos_session_id": self.session.id}
        ).run()
        self.assertIn(self.enc.state, ["finished", "onleave"])
        self.assertTrue(
            self.enc.sale_order_ids.mapped("order_line").filtered(
                lambda r: r.laboratory_event_id
            )
        )
        self.assertGreater(
            sum(
                a.amount
                for a in self.enc.sale_order_ids.mapped("order_line")
                .filtered(lambda r: r.laboratory_event_id)
                .mapped("agents")
            ),
            0,
        )
