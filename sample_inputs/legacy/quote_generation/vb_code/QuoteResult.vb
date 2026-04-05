Imports System.Collections.Generic

Namespace LegacyModernization.QuoteGeneration.Backend.Models
    Public Class QuoteResult
        Public Property QuoteId As Integer
        Public Property FinalPremium As Decimal
        Public Property BasePremium As Decimal
        Public Property DiscountAmount As Decimal
        Public Property TaxAmount As Decimal
        Public Property RiskFactor As Decimal
        Public Property CountryAdjustmentAmount As Decimal
        Public Property Notes As New List(Of String)()
    End Class
End Namespace
