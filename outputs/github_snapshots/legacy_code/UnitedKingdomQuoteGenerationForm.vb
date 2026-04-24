Namespace LegacyModernization.QuoteGeneration.Forms
    Public Class UnitedKingdomQuoteGenerationForm
        Inherits BaseQuoteGenerationForm

        Protected Overrides ReadOnly Property CountryCode As String = "GB"
        Protected Overrides ReadOnly Property CountryDisplayName As String = "United Kingdom"

        Protected Overrides Sub ConfigureCountryDefaults()
            MyBase.ConfigureCountryDefaults()
            cboPolicyType.SelectedItem = "TRAVEL"
            lblCountryHint.Text = "UK quotes apply IPT handling and annual premium collections rules."
        End Sub
    End Class
End Namespace
