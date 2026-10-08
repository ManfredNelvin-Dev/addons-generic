# Copyright 2026 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("digest_membership_donations", "post_install", "-at_install")
class TestDigestMembershipDonations(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company

        cls.digest = cls.env["digest.digest"].create(
            {
                "name": "Test Digest Donations",
                "periodicity": "daily",
                "company_id": cls.company.id,
                "kpi_membership_donations": True,
                "kpi_membership_donations_amount": True,
            }
        )

    def test_kpi_membership_donations_value(self):
        payment_transaction = self.env["payment.transaction"]

        with patch.dict(
            payment_transaction._fields,
            {"is_donation": object()},
            clear=False,
        ):
            with patch.object(
                type(payment_transaction),
                "search_count",
                return_value=5,
            ):
                self.digest._compute_kpi_membership_donations_value()

                self.assertEqual(
                    self.digest.kpi_membership_donations_value,
                    5,
                )

    def test_kpi_membership_donations_amount_value(self):
        payment_transaction = self.env["payment.transaction"]

        with patch.dict(
            payment_transaction._fields,
            {"is_donation": object()},
            clear=False,
        ):
            mock_tx = self.env["payment.transaction"]
            with patch.object(
                type(payment_transaction),
                "search",
                return_value=mock_tx,
            ):
                with patch.object(
                    type(mock_tx),
                    "mapped",
                    return_value=[100.0, 200.0],
                ):
                    self.digest._compute_kpi_membership_donations_amount_value()

                    self.assertEqual(
                        self.digest.kpi_membership_donations_amount_value,
                        300.0,
                    )
