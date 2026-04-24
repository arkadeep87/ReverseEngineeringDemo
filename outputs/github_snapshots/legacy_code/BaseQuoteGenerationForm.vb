Imports System.Windows.Forms
Imports LegacyModernization.QuoteGeneration.Backend.Facade
Imports LegacyModernization.QuoteGeneration.Backend.Models

Namespace LegacyModernization.QuoteGeneration.Forms
    Public MustInherit Class BaseQuoteGenerationForm
        Inherits Form

        Protected ReadOnly txtCustomerId As New TextBox()
        Protected ReadOnly txtAge As New TextBox()
        Protected ReadOnly txtCoverage As New TextBox()
        Protected ReadOnly cboPolicyType As New ComboBox()
        Protected ReadOnly cboPaymentFrequency As New ComboBox()
        Protected ReadOnly cboCustomerSegment As New ComboBox()
        Protected ReadOnly chkGdprConsent As New CheckBox()
        Protected ReadOnly lblCountryHint As New Label()
        Protected ReadOnly btnGenerate As New Button()

        Private ReadOnly _facade As New QuoteSubmissionFacade()

        Protected Sub New()
            Text = FormTitle
            Width = 720
            Height = 430
            BuildControls()
            ConfigureCountryDefaults()
        End Sub

        Protected MustOverride ReadOnly Property CountryCode As String
        Protected MustOverride ReadOnly Property CountryDisplayName As String
        Protected Overridable ReadOnly Property FormTitle As String
            Get
                Return CountryDisplayName & " Quote Generation"
            End Get
        End Property

        Private Sub BuildControls()
            Dim lblCustomerId As New Label() With {.Left = 30, .Top = 30, .Width = 140, .Text = "Customer Id"}
            txtCustomerId.Left = 180
            txtCustomerId.Top = 25
            txtCustomerId.Width = 180

            Dim lblAge As New Label() With {.Left = 30, .Top = 70, .Width = 140, .Text = "Customer Age"}
            txtAge.Left = 180
            txtAge.Top = 65
            txtAge.Width = 90

            Dim lblCoverage As New Label() With {.Left = 30, .Top = 110, .Width = 140, .Text = "Coverage Amount"}
            txtCoverage.Left = 180
            txtCoverage.Top = 105
            txtCoverage.Width = 180

            Dim lblPolicy As New Label() With {.Left = 30, .Top = 150, .Width = 140, .Text = "Policy Type"}
            cboPolicyType.Left = 180
            cboPolicyType.Top = 145
            cboPolicyType.Width = 180
            cboPolicyType.Items.AddRange(New Object() {"HEALTH", "TRAVEL", "FAMILY", "CORPORATE"})

            Dim lblFrequency As New Label() With {.Left = 30, .Top = 190, .Width = 140, .Text = "Payment Frequency"}
            cboPaymentFrequency.Left = 180
            cboPaymentFrequency.Top = 185
            cboPaymentFrequency.Width = 180
            cboPaymentFrequency.Items.AddRange(New Object() {"MONTHLY", "QUARTERLY", "ANNUAL"})

            Dim lblSegment As New Label() With {.Left = 30, .Top = 230, .Width = 140, .Text = "Customer Segment"}
            cboCustomerSegment.Left = 180
            cboCustomerSegment.Top = 225
            cboCustomerSegment.Width = 180
            cboCustomerSegment.Items.AddRange(New Object() {"STANDARD", "LOYALTY_GOLD", "EMPLOYEE"})

            chkGdprConsent.Left = 180
            chkGdprConsent.Top = 265
            chkGdprConsent.Width = 240
            chkGdprConsent.Text = "GDPR Consent Confirmed"

            lblCountryHint.Left = 30
            lblCountryHint.Top = 305
            lblCountryHint.Width = 620
            lblCountryHint.Height = 35

            btnGenerate.Left = 180
            btnGenerate.Top = 345
            btnGenerate.Width = 160
            btnGenerate.Text = "Generate Quote"
            AddHandler btnGenerate.Click, AddressOf OnGenerateQuote

            Controls.AddRange(New Control() {
                lblCustomerId, txtCustomerId,
                lblAge, txtAge,
                lblCoverage, txtCoverage,
                lblPolicy, cboPolicyType,
                lblFrequency, cboPaymentFrequency,
                lblSegment, cboCustomerSegment,
                chkGdprConsent, lblCountryHint, btnGenerate
            })
        End Sub

        Protected Overridable Sub ConfigureCountryDefaults()
            cboPolicyType.SelectedItem = "HEALTH"
            cboPaymentFrequency.SelectedItem = "ANNUAL"
            cboCustomerSegment.SelectedItem = "STANDARD"
            lblCountryHint.Text = "Country specific quote adjustments are active for " & CountryDisplayName & "."
        End Sub

        Private Sub OnGenerateQuote(sender As Object, e As EventArgs)
            Dim request As New QuoteRequest With {
                .CustomerId = txtCustomerId.Text,
                .CustomerAge = Integer.Parse(txtAge.Text),
                .CountryCode = CountryCode,
                .PolicyType = CStr(cboPolicyType.SelectedItem),
                .CoverageAmount = Decimal.Parse(txtCoverage.Text),
                .PaymentFrequency = CStr(cboPaymentFrequency.SelectedItem),
                .CustomerSegment = CStr(cboCustomerSegment.SelectedItem),
                .GdprConsentGranted = chkGdprConsent.Checked
            }

            Dim result = _facade.SubmitQuote(request)
            MessageBox.Show(
                "Quote Id: " & result.QuoteId & Environment.NewLine &
                "Premium: " & result.FinalPremium.ToString("0.00") & Environment.NewLine &
                "Country Adjustment: " & result.CountryAdjustmentAmount.ToString("0.00"),
                CountryDisplayName & " quote generated"
            )
        End Sub
    End Class
End Namespace
