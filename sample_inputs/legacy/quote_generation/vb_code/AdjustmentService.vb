
Public Class AdjustmentService

    ' New method that explicitly uses country_tax_rules via SP
    Public Function GetCountryTax(countryCode As String, premiumAmount As Decimal) As Decimal

        Dim taxAmount As Decimal

        taxAmount = ExecuteScalar("sp_get_country_tax", New With {
            .country_code = countryCode,
            .premium_amount = premiumAmount
        })

        Return taxAmount

    End Function

End Class
