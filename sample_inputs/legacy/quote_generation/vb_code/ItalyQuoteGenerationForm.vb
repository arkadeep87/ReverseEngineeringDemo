Namespace LegacyModernization.QuoteGeneration.Forms
    Public Class ItalyQuoteGenerationForm
        Inherits BaseQuoteGenerationForm

        Protected Overrides ReadOnly Property CountryCode As String = "IT"
        Protected Overrides ReadOnly Property CountryDisplayName As String = "Italy"

        Protected Overrides Sub ConfigureCountryDefaults()
            MyBase.ConfigureCountryDefaults()
            cboPolicyType.SelectedItem = "FAMILY"
            lblCountryHint.Text = "Italy quotes add stamp duty and family policy loyalty adjustments."
        End Sub
    End Class
End Namespace
