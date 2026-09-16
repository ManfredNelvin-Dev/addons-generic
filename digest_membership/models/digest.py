# Copyright 2026 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = "digest.digest"

    kpi_membership_new_members = fields.Boolean("New Members")
    kpi_membership_new_members_value = fields.Integer(
        compute="_compute_kpi_membership_new_members_value"
    )

    kpi_membership_donations = fields.Boolean("Donation")
    kpi_membership_donations_value = fields.Integer(
        compute="_compute_kpi_membership_donations_value"
    )

    kpi_membership_donations_amount = fields.Boolean(
        "Donation Amount",
        compute="_compute_kpi_membership_donations_amount",
    )
    kpi_membership_donations_amount_value = fields.Monetary(
        compute="_compute_kpi_membership_donations_amount_value",
        currency_field="currency_id",
    )

    kpi_membership_activity = fields.Boolean("Activity")
    kpi_membership_activity_value = fields.Integer(
        compute="_compute_kpi_membership_activity_value"
    )

    def _check_kpi_access(self):
        if not self.env.user.has_group("base.group_user"):
            raise AccessError(_("You do not have access to compute this KPI."))

    def _get_donation_domain(self, company, start, end):
        return [
            ("company_id", "=", company.id),
            ("create_date", ">=", start),
            ("create_date", "<", end),
            ("state", "=", "done"),
            ("is_donation", "=", True),
        ]

    def _compute_kpi_membership_new_members_value(self):
        self._check_kpi_access()

        for record in self:
            start, end, company = record._get_kpi_compute_parameters()

            record.kpi_membership_new_members_value = self.env[
                "res.partner"
            ].search_count(
                [
                    ("company_id", "in", (False, company.id)),
                    ("create_date", ">=", start),
                    ("create_date", "<", end),
                    ("membership_state", "in", ["invoiced", "paid", "free"]),
                ]
            )

    def _compute_kpi_membership_donations_amount(self):
        for record in self:
            record.kpi_membership_donations_amount = record.kpi_membership_donations

    def _compute_kpi_membership_donations_amount_value(self):
        self._check_kpi_access()

        payment_transaction = self.env["payment.transaction"]

        for record in self:
            start, end, company = record._get_kpi_compute_parameters()

            if "is_donation" not in payment_transaction._fields:
                record.kpi_membership_donations_amount_value = 0.0
                continue

            domain = self._get_donation_domain(company, start, end)
            transactions = payment_transaction.search(domain)

            record.kpi_membership_donations_amount_value = sum(
                transactions.mapped("amount")
            )

    def _compute_kpi_membership_donations_value(self):
        self._check_kpi_access()

        payment_transaction = self.env["payment.transaction"]

        for record in self:
            start, end, company = record._get_kpi_compute_parameters()

            if "is_donation" not in payment_transaction._fields:
                record.kpi_membership_donations_value = 0
                continue

            domain = self._get_donation_domain(company, start, end)

            record.kpi_membership_donations_value = payment_transaction.search_count(
                domain
            )

    def _compute_kpi_membership_activity_value(self):
        self._check_kpi_access()

        for record in self:
            start, end, company = record._get_kpi_compute_parameters()

            if "membership.activity" not in self.env:
                record.kpi_membership_activity_value = 0
                continue

            record.kpi_membership_activity_value = self.env[
                "membership.activity"
            ].search_count(
                [
                    ("date", ">=", start),
                    ("date", "<", end),
                ]
            )
