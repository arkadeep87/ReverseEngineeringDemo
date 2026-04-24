Namespace LegacyModernization.QuoteGeneration.Forms
    Public Class GermanyQuoteGenerationForm
        Inherits BaseQuoteGenerationForm

        Protected Overrides ReadOnly Property CountryCode As String = "DE"
        Protected Overrides ReadOnly Property CountryDisplayName As String = "Germany"

        Protected Overrides Sub ConfigureCountryDefaults()
            MyBase.ConfigureCountryDefaults()
            cboPolicyType.SelectedItem = "HEALTH"
            lblCountryHint.Text = "Germany quotes apply insurance tax and social surcharge checks."
        End Sub
    End Class
End Namespace
