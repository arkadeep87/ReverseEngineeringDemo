Namespace LegacyModernization.QuoteGeneration.Forms
    Public Class SpainQuoteGenerationForm
        Inherits BaseQuoteGenerationForm

        Protected Overrides ReadOnly Property CountryCode As String = "ES"
        Protected Overrides ReadOnly Property CountryDisplayName As String = "Spain"

        Protected Overrides Sub ConfigureCountryDefaults()
            MyBase.ConfigureCountryDefaults()
            cboPolicyType.SelectedItem = "TRAVEL"
            lblCountryHint.Text = "Spain quotes include regional duty and travel assistance handling."
        End Sub
    End Class
End Namespace
