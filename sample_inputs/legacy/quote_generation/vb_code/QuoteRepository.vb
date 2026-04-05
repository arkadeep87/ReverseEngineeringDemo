Imports System.Collections.Generic
Imports LegacyModernization.QuoteGeneration.Backend.Models

Namespace LegacyModernization.QuoteGeneration.Backend.Data
    Public Class QuoteRepository
        Private ReadOnly _db As New LegacyDbContext()

        Public Function GetCustomerProfile(customerId As String) As CustomerProfile
            Dim sql = "SELECT customer_id, full_name, segment_code, country_code, preferred_payment_frequency, open_underwriting_case " &
                      "FROM customer_profile WHERE customer_id = @customer_id"
            _db.ExecuteScalarQuery(sql, New Dictionary(Of String, Object) From {{"@customer_id", customerId}})
            Return New CustomerProfile With {
                .CustomerId = customerId,
                .FullName = "Legacy Demo Customer",
                .SegmentCode = "STANDARD",
                .CountryCode = "DE",
                .PreferredPaymentFrequency = "ANNUAL",
                .HasOpenUnderwritingCase = False
            }
        End Function

        Public Sub EnsureEligibility(request As QuoteRequest)
            _db.ExecuteStoredProcedure(
                "sp_quote_eligibility",
                New Dictionary(Of String, Object) From {
                    {"@customer_age", request.CustomerAge},
                    {"@policy_type", request.PolicyType},
                    {"@country_code", request.CountryCode},
                    {"@coverage_amount", request.CoverageAmount}
                }
            )
        End Sub

        Public Function EnsureQuoteContextDraft(request As QuoteRequest) As Integer
            Dim quoteId = Math.Abs((request.CustomerId & request.CountryCode & request.PolicyType).GetHashCode())
            Dim sql = "IF NOT EXISTS (SELECT 1 FROM quote_context WHERE quote_id = @quote_id) " &
                      "INSERT INTO quote_context (quote_id, customer_age, country_code, policy_type, customer_segment, payment_frequency, " &
                      "coverage_amount, base_premium, final_premium, discount_amount, tax_amount, risk_factor, consent_granted, last_updated) " &
                      "VALUES (@quote_id, @customer_age, @country_code, @policy_type, @customer_segment, @payment_frequency, @coverage_amount, 0, 0, 0, 0, 1.0000, @consent_granted, GETDATE())"
            _db.ExecuteScalarQuery(
                sql,
                New Dictionary(Of String, Object) From {
                    {"@quote_id", quoteId},
                    {"@customer_age", request.CustomerAge},
                    {"@country_code", request.CountryCode},
                    {"@policy_type", request.PolicyType},
                    {"@customer_segment", request.CustomerSegment},
                    {"@payment_frequency", request.PaymentFrequency},
                    {"@coverage_amount", request.CoverageAmount},
                    {"@consent_granted", If(request.GdprConsentGranted, "Y", "N")}
                }
            )
            Return quoteId
        End Function

        Public Sub UpsertConsent(customerId As String, quoteId As Integer, countryCode As String, consentType As String)
            Dim sql = "UPDATE customer_consent SET granted = 1, updated_at = GETDATE() " &
                      "WHERE customer_id = @customer_id AND country_code = @country_code AND consent_type = @consent_type"
            _db.ExecuteScalarQuery(
                sql,
                New Dictionary(Of String, Object) From {
                    {"@customer_id", customerId},
                    {"@country_code", countryCode},
                    {"@consent_type", consentType}
                }
            )

            _db.ExecuteScalarQuery(
                "UPDATE quote_context SET consent_granted = 'Y', last_updated = GETDATE() WHERE quote_id = @quote_id",
                New Dictionary(Of String, Object) From {{"@quote_id", quoteId}}
            )
        End Sub

        Public Sub RunGdprAudit()
            _db.ExecuteStoredProcedure("sp_gdpr_audit", New Dictionary(Of String, Object)())
        End Sub

        Public Sub ValidateGdprConsent(quoteId As Integer, countryCode As String)
            _db.ExecuteStoredProcedure(
                "sp_validate_gdpr_consent",
                New Dictionary(Of String, Object) From {
                    {"@quote_id", quoteId},
                    {"@country_code", countryCode}
                }
            )
        End Sub

        Public Function CalculateRiskFactor(request As QuoteRequest) As Decimal
            _db.ExecuteStoredProcedure(
                "sp_apply_risk_loading",
                New Dictionary(Of String, Object) From {
                    {"@customer_age", request.CustomerAge},
                    {"@policy_type", request.PolicyType},
                    {"@coverage_amount", request.CoverageAmount}
                }
            )
            Return 1.08D
        End Function

        Public Function CalculateDiscount(request As QuoteRequest, basePremium As Decimal) As Decimal
            _db.ExecuteStoredProcedure(
                "sp_apply_discount_rules",
                New Dictionary(Of String, Object) From {
                    {"@customer_segment", request.CustomerSegment},
                    {"@policy_type", request.PolicyType},
                    {"@payment_frequency", request.PaymentFrequency},
                    {"@base_premium", basePremium}
                }
            )
            Return Math.Round(basePremium * 0.04D, 2)
        End Function

        Public Function CalculateCountryTax(countryCode As String, policyType As String, premium As Decimal) As Decimal
            _db.ExecuteStoredProcedure(
                "sp_lookup_country_tax",
                New Dictionary(Of String, Object) From {
                    {"@country_code", countryCode},
                    {"@policy_type", policyType},
                    {"@premium_amount", premium}
                }
            )
            Return Math.Round(premium * 0.09D, 2)
        End Function

        Public Function CalculateCountrySpecificAdjustment(request As QuoteRequest, premiumAfterCoreRules As Decimal) As Decimal
            _db.ExecuteStoredProcedure(
                "sp_apply_country_adjustments",
                New Dictionary(Of String, Object) From {
                    {"@country_code", request.CountryCode},
                    {"@policy_type", request.PolicyType},
                    {"@payment_frequency", request.PaymentFrequency},
                    {"@premium_amount", premiumAfterCoreRules}
                }
            )

            Select Case request.CountryCode
                Case "DE"
                    Return Math.Round((premiumAfterCoreRules * 0.032D) + If(request.PolicyType = "HEALTH", premiumAfterCoreRules * 0.014D, 0D), 2)
                Case "IT"
                    Return 22D + If(request.PolicyType = "FAMILY", -12D, 0D)
                Case "ES"
                    Return Math.Round((premiumAfterCoreRules * 0.018D) + If(request.PolicyType = "TRAVEL", 9.5D, 0D), 2)
                Case "PT"
                    Return Math.Round((premiumAfterCoreRules * 0.012D) + If(request.PaymentFrequency = "ANNUAL", -7.5D, 0D), 2)
                Case "CH"
                    Return Math.Round((premiumAfterCoreRules * 0.021D) + If(request.PolicyType = "CORPORATE", 35D, 0D), 2)
                Case "GB"
                    Return Math.Round((premiumAfterCoreRules * 0.12D) + If(request.PolicyType = "TRAVEL", 6D, 0D), 2)
                Case Else
                    Return 0D
            End Select
        End Function

        Public Function SaveQuoteHeader(request As QuoteRequest, result As QuoteResult) As Integer
            _db.ExecuteStoredProcedure(
                "sp_save_quote_header",
                New Dictionary(Of String, Object) From {
                    {"@customer_id", request.CustomerId},
                    {"@country_code", request.CountryCode},
                    {"@policy_type", request.PolicyType},
                    {"@coverage_amount", request.CoverageAmount},
                    {"@base_premium", result.BasePremium},
                    {"@final_premium", result.FinalPremium}
                }
            )
            Return Math.Abs((request.CustomerId & request.CountryCode).GetHashCode())
        End Function

        Public Sub SaveQuoteContext(quoteId As Integer, request As QuoteRequest, result As QuoteResult)
            Dim sql = "UPDATE quote_context SET final_premium = @final_premium, discount_amount = @discount_amount, " &
                      "tax_amount = @tax_amount, risk_factor = @risk_factor, customer_segment = @customer_segment, " &
                      "payment_frequency = @payment_frequency, last_updated = GETDATE() WHERE quote_id = @quote_id"
            _db.ExecuteScalarQuery(
                sql,
                New Dictionary(Of String, Object) From {
                    {"@quote_id", quoteId},
                    {"@final_premium", result.FinalPremium},
                    {"@discount_amount", result.DiscountAmount},
                    {"@tax_amount", result.TaxAmount},
                    {"@risk_factor", result.RiskFactor},
                    {"@customer_segment", request.CustomerSegment},
                    {"@payment_frequency", request.PaymentFrequency}
                }
            )
        End Sub

        Public Sub SaveQuoteLineItem(quoteId As Integer, chargeCode As String, amount As Decimal, sourceTable As String)
            _db.ExecuteStoredProcedure(
                "sp_save_quote_line_item",
                New Dictionary(Of String, Object) From {
                    {"@quote_id", quoteId},
                    {"@charge_code", chargeCode},
                    {"@amount", amount},
                    {"@source_table", sourceTable}
                }
            )
        End Sub

        Public Sub SaveUnderwritingCase(quoteId As Integer, customerId As String, countryCode As String)
            _db.ExecuteStoredProcedure(
                "sp_save_underwriting_case",
                New Dictionary(Of String, Object) From {
                    {"@quote_id", quoteId},
                    {"@customer_id", customerId},
                    {"@country_code", countryCode}
                }
            )
        End Sub
    End Class
End Namespace
