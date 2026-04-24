Imports System.Collections.Generic

Namespace LegacyModernization.QuoteGeneration.Backend.Data
    Public Class ReferenceDataRepository
        Private ReadOnly _db As New LegacyDbContext()

        Public Function GetPolicyCatalog(policyType As String) As Object
            Dim sql = "SELECT policy_type, base_rate, minimum_cover, maximum_cover FROM policy_catalog WHERE policy_type = @policy_type"
            _db.ExecuteScalarQuery(sql, New Dictionary(Of String, Object) From {{"@policy_type", policyType}})
            Return New With {.policy_type = policyType}
        End Function

        Public Function GetPaymentSchedule(paymentFrequency As String) As Object
            Dim sql = "SELECT schedule_code, collection_days, surcharge_pct FROM payment_schedule WHERE schedule_code = @schedule_code"
            _db.ExecuteScalarQuery(sql, New Dictionary(Of String, Object) From {{"@schedule_code", paymentFrequency}})
            Return New With {.schedule_code = paymentFrequency}
        End Function

        Public Function GetCountryRule(countryCode As String, policyType As String) As Object
            Dim sql = "SELECT country_code, policy_type, tax_rate, is_eu_member FROM country_tax_rules " &
                      "WHERE country_code = @country_code AND policy_type IN (@policy_type, 'DEFAULT')"
            _db.ExecuteScalarQuery(
                sql,
                New Dictionary(Of String, Object) From {
                    {"@country_code", countryCode},
                    {"@policy_type", policyType}
                }
            )
            Return New With {.country_code = countryCode, .policy_type = policyType}
        End Function

        Public Function GetBasePremium(policyType As String, coverageAmount As Decimal) As Decimal
            GetPolicyCatalog(policyType)
            Return Math.Round((coverageAmount / 1000D) * 4.25D, 2)
        End Function
    End Class
End Namespace
