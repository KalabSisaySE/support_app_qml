import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {
    id: helpRoot

    // --- Vlastnosti pre podmienený text (opravené na jeden riadok) ---

    property string clientHelpText: "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li { white-space: pre-wrap; } h3 { color: #55aaff; margin-bottom: 5px; } ul { padding-left: 20px; }</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\"><p>Vitajte v aplikácii Macrosoft Support. Táto príručka vám pomôže pochopiť a efektívne využívať všetky jej funkcie.</p><h3>1. Povolenia pre Kameru a Mikrofón</h3><p>Táto funkcia slúži na udelenie prístupu našej webovej stránke k vašej kamere a mikrofónu priamo z aplikácie, čo zjednodušuje prípravu na online stretnutia.</p><ul><li>Prejdite na kartu <b>'Povolenia'</b> v ľavom menu.</li><li>Nájdete tu tlačidlá na povolenie prístupu len pre mikrofón alebo pre mikrofón aj kameru súčasne.</li><li>Stlačením tlačidla <b>'Povoliť všetko'</b> udelíte prístup obom zariadeniam.</li><li>Tlačidlom <b>'Otvoriť webstránku'</b> môžete skontrolovať stav povolení priamo na našej stránke.</li></ul><p>Stav úspešnosti operácie môžete sledovať v informačnom paneli na karte <b>'Informácie'</b>.</p><h3>2. Vzdialená Podpora (MacrosoftConnectQuickSupport)</h3><p>Táto časť aplikácie je určená na správu nástroja pre vzdialenú pomoc. Umožňuje lektorovi pripojiť sa k vášmu počítaču a pomôcť vám s technickými problémami.</p><ul><li>Prejdite na kartu <b>'Služby'</b> v ľavom menu.</li><li><b>Inštalácia:</b> Ak aplikácia ešte nie je nainštalovaná, použite tlačidlo <b>'Inštalovať'</b>. Po úspešnej inštalácii sa tlačidlo zmení na <b>'Odinštalovať'</b>.</li><li><b>Spustenie služby:</b> Pre umožnenie vzdialeného prístupu je potrebné, aby bežala služba na pozadí. Službu môžete spustiť a zastaviť tlačidlom <b>'Spustiť/Zastaviť službu'</b>.</li><li><b>Získanie ID:</b> Keď vás lektor požiada o prístupové ID, kliknite na tlačidlo <b>'Získať ID'</b>. Vaše unikátne ID sa zobrazí v tejto záložke a tiež na hlavnej stránke <b>'Informácie'</b>.</li></ul><p>Všetky stavy (inštalácia, bežiaca služba) sú prehľadne zobrazené pomocou indikátorov na tejto stránke a tiež na karte <b>'Informácie'</b>.</p></body></html>"

    property string lecturerHelpText: "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\n" +
        "<html>\n" +
        "<head>\n" +
        "    <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">\n" +
        "    <title>Užívateľská príručka aplikácie Macrosoft Support</title>\n" +
        "    <style type=\"text/css\">\n" +
        "        body {\n" +
        "            background-color: #1c1e22; \n" +
        "            font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif;\n" +
        "            font-size: 16px;\n" +
        "            line-height: 1.7;\n" +
        "            color: #d1d2d2; \n" +
        "            margin: 0;\n" +
        "            padding: 20px;\n" +
        "        }\n" +
        "        .container {\n" +
        "            max-width: 800px;\n" +
        "            margin: 20px auto;\n" +
        "            background-color: #2d323a;\n" +
        "            border: 1px solid #4a5059;\n" +
        "            border-radius: 8px;\n" +
        "            padding: 30px 40px;\n" +
        "        }\n" +
        "        h1, h2 {\n" +
        "            color: #56bcc2; \n" +
        "            font-weight: 400; \n" +
        "        }\n" +
        "        h1 {\n" +
        "            font-size: 28px;\n" +
        "            text-align: center;\n" +
        "            border-bottom: 1px solid #4a5059;\n" +
        "            padding-bottom: 20px;\n" +
        "            margin-top: 10px;\n" +
        "            margin-bottom: 30px;\n" +
        "        }\n" +
        "        h2 {\n" +
        "            font-size: 22px;\n" +
        "            padding-bottom: 5px;\n" +
        "            margin-top: 40px;\n" +
        "            border-bottom: none;\n" +
        "        }\n" +
        "        h3 {\n" +
        "            color: #e5e6e6;\n" +
        "            font-weight: 600;\n" +
        "            font-size: 18px;\n" +
        "            margin-top: 40px;\n" +
        "            margin-bottom: 20px;\n" +
        "        }\n" +
        "        p {\n" +
        "            margin: 15px 0;\n" +
        "        }\n" +
        "        ol, ul {\n" +
        "            padding-left: 25px;\n" +
        "        }\n" +
        "        li {\n" +
        "            padding-left: 10px;\n" +
        "            margin-bottom: 15px;\n" +
        "        }\n" +
        "        li::marker {\n" +
        "            color: #56bcc2;\n" +
        "            font-weight: 600;\n" +
        "        }\n" +
        "        ul ul {\n" +
        "            margin-top: 15px;\n" +
        "            padding-left: 30px;\n" +
        "            /* FINÁLNA ÚPRAVA: Zmena odrážok na prázdne krúžky */\n" +
        "            list-style-type: circle; \n" +
        "        }\n" +
        "        strong {\n" +
        "            color: #56bcc2;\n" +
        "            font-weight: normal;\n" +
        "        }\n" +
        "        li > strong {\n" +
        "            font-weight: 600;\n" +
        "        }\n" +
        "        code {\n" +
        "            font-family: inherit;\n" +
        "            background-color: #3c424b;\n" +
        "            color: #d1d2d2;\n" +
        "            padding: 3px 8px;\n" +
        "            border-radius: 4px;\n" +
        "            font-size: 15px;\n" +
        "        }\n" +
        "        hr {\n" +
        "            border: 0;\n" +
        "            height: 1px;\n" +
        "            background: #4a5059;\n" +
        "            margin: 40px 0;\n" +
        "        }\n" +
        "    </style>\n" +
        "</head>\n" +
        "<body>\n" +
        "\n" +
        "<div class=\"container\">\n" +
        "\n" +
        "    <h1>Užívateľská príručka aplikácie Macrosoft Support</h1>\n" +
        "    <p>Vitajte! Táto príručka vás prevedie všetkými funkciami aplikácie Macrosoft Support, ktorá bola navrhnutá tak, aby zabezpečila hladký a bezproblémový priebeh vášho online školenia.</p>\n" +
        "    <hr>\n" +
        "    \n" +
        "    <h2>Rýchle Nastavenie: Konfigurácia na 1 klik</h2>\n" +
        "    <p>Pre najjednoduchšiu a najrýchlejšiu prípravu odporúčame použiť funkciu <strong>Konfigurácia na 1 klik</strong>. Nájdete ju v sekciách <code>Inštalácia a Spustenie</code> a <code>Povolenia</code>.</p>\n" +
        "    <ol>\n" +
        "        <li><strong>Povolí prístup</strong> pre mikrofón a webkameru, ktoré sú nevyhnutné pre komunikáciu počas školenia.</li>\n" +
        "        <li><strong>Nainštaluje a spustí aplikáciu</strong> pre vzdialenú podporu (MacrosoftConnectQuickSupport), ktorá umožní lektorovi pripojiť sa na vašu obrazovku a pomôcť vám v prípade technických problémov.</li>\n" +
        "    </ol>\n" +
        "    <p>Po stlačení tohto tlačidla bude váš systém kompletne pripravený na školenie.</p>\n" +
        "    <hr>\n" +
        "\n" +
        "    <h2>Prehľad jednotlivých sekcií aplikácie</h2>\n" +
        "\n" +
        "    <h3>1. Prehľad Informácií</h3>\n" +
        "    <p>Toto je vaša hlavná obrazovka, kde nájdete súhrn všetkých dôležitých informácií a stavov:</p>\n" +
        "    <ul>\n" +
        "        <li><strong>Vaše meno a ID:</strong> Unikátne údaje slúžiace na vašu identifikáciu.</li>\n" +
        "        <li><strong>Stavové indikátory:</strong> Farebné bodky vám rýchlo ukážu stav jednotlivých komponentov:\n" +
        "            <ul>\n" +
        "                <li>Zelená: Všetko je v poriadku a plne funkčné.</li>\n" +
        "                <li>Oranžová/Červená: Vyžaduje sa vaša pozornosť alebo akcia (napr. udelenie povolení).</li>\n" +
        "            </ul>\n" +
        "        </li>\n" +
        "        <li><strong>Tlačidlo \"Otvoriť webstránku\":</strong> Toto tlačidlo vás jedným kliknutím presmeruje do vášho klientskeho účtu. Tu sa môžete pripojiť na <strong>živé online školenie</strong> alebo si pozrieť <strong>záznamy</strong> z už absolvovaných kurzov.</li>\n" +
        "    </ul>\n" +
        "\n" +
        "    <h3>2. Inštalácia a Spustenie (Vzdialená Podpora)</h3>\n" +
        "    <p>Táto sekcia slúži na správu nástroja <strong>MacrosoftConnectQuickSupport</strong>, ktorý umožňuje lektorovi poskytnúť vám technickú pomoc na diaľku priamo na vašom počítači.</p>\n" +
        "    <ul>\n" +
        "        <li><strong>Odinštalovať:</strong> Ak je aplikácia nainštalovaná, toto tlačidlo ju bezpečne odstráni.</li>\n" +
        "        <li><strong>Spustiť / Zastaviť službu:</strong> Spúšťa alebo zastavuje službu na pozadí, ktorá je potrebná pre pripojenie lektora. Pre úspešné pripojenie musí byť služba spustená.</li>\n" +
        "        <li><strong>Získať ID:</strong> Kliknutím na toto tlačidlo zobrazíte unikátny prístupový kód (ID), ktoré bude mať lektor automaticky dostupný cez našu platformu.</li>\n" +
        "    </ul>\n" +
        "    \n" +
        "    <h3>3. Povolenia (Prístup k Mikrofónu a Kamere)</h3>\n" +
        "    <p>Pre plnohodnotnú účasť na online školení je nevyhnutné povoliť prístup k vášmu mikrofónu a webkamere.</p>\n" +
        "    <ul>\n" +
        "        <li><strong>Povoliť len Mikrofón:</strong> Udelí prístup iba vášmu mikrofónu.</li>\n" +
        "        <li><strong>Povoliť všetko:</strong> Udelí prístup mikrofónu aj webkamere súčasne.</li>\n" +
        "    </ul>\n" +
        "    \n" +
        "    <hr>\n" +
        "    \n" +
        "    <p style=\"text-align:center; font-style:italic; color: #a0a0a0;\">Veríme, že vám táto príručka pomohla. V prípade akýchkoľvek otázok sa neváhajte obrátiť na našu podporu. Prajeme vám úspešné školenie.</p>\n" +
        "    \n" +
        "</div>\n" +
        "\n" +
        "</body>\n" +
        "</html>"


    Rectangle {
        id: rectangle
        color: "#2c313c"
        anchors.fill: parent

        Rectangle {
            id: rectangleVisible
            color: "#1d2128"
            radius: 4
            anchors.fill: parent
            anchors.margins: 20

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 15

                Label {
                    id: labelTextName
                    color: "#c3cbdd"
                    // Podmienené nastavenie titulku na základe backend vlastnosti
                    text: backend.is_user_lectoure
                          ? qsTr("Návod na Používanie Aplikácie (Lektor)")
                          : qsTr("Návod na Používanie Aplikácie (Klient)")
                    Layout.alignment: Qt.AlignHCenter
                    font.pointSize: 14
                    font.bold: true
                }

                ScrollView {
                    id: scrollView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true

                    TextArea {
                        id: textHome
                        readOnly: true
                        wrapMode: Text.WordWrap
                        color: "#a9b2c8"
                        font.pointSize: 10
                        textFormat: Text.RichText
                        background: Rectangle { color: "transparent" }
                        // Podmienené nastavenie obsahu na základe backend vlastnosti
                        text: backend.is_user_lectoure
                              ? helpRoot.lecturerHelpText
                              : helpRoot.clientHelpText
                    }
                }
            }
        }
    }
}