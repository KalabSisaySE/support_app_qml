import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {
    id: helpRoot

    // --- Vlastnosti pre podmienený text (opravené na jeden riadok) ---

    property string clientHelpText: "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li { white-space: pre-wrap; } h3 { color: #55aaff; margin-bottom: 5px; } ul { padding-left: 20px; }</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\"><p>Vitajte v aplikácii Macrosoft Support. Táto príručka vám pomôže pochopiť a efektívne využívať všetky jej funkcie.</p><h3>1. Povolenia pre Kameru a Mikrofón</h3><p>Táto funkcia slúži na udelenie prístupu našej webovej stránke k vašej kamere a mikrofónu priamo z aplikácie, čo zjednodušuje prípravu na online stretnutia.</p><ul><li>Prejdite na kartu <b>'Povolenia'</b> v ľavom menu.</li><li>Nájdete tu tlačidlá na povolenie prístupu len pre mikrofón alebo pre mikrofón aj kameru súčasne.</li><li>Stlačením tlačidla <b>'Povoliť všetko'</b> udelíte prístup obom zariadeniam.</li><li>Tlačidlom <b>'Otvoriť webstránku'</b> môžete skontrolovať stav povolení priamo na našej stránke.</li></ul><p>Stav úspešnosti operácie môžete sledovať v informačnom paneli na karte <b>'Informácie'</b>.</p><h3>2. Vzdialená Podpora (MacrosoftConnectQuickSupport)</h3><p>Táto časť aplikácie je určená na správu nástroja pre vzdialenú pomoc. Umožňuje lektorovi pripojiť sa k vášmu počítaču a pomôcť vám s technickými problémami.</p><ul><li>Prejdite na kartu <b>'Služby'</b> v ľavom menu.</li><li><b>Inštalácia:</b> Ak aplikácia ešte nie je nainštalovaná, použite tlačidlo <b>'Inštalovať'</b>. Po úspešnej inštalácii sa tlačidlo zmení na <b>'Odinštalovať'</b>.</li><li><b>Spustenie služby:</b> Pre umožnenie vzdialeného prístupu je potrebné, aby bežala služba na pozadí. Službu môžete spustiť a zastaviť tlačidlom <b>'Spustiť/Zastaviť službu'</b>.</li><li><b>Získanie ID:</b> Keď vás lektor požiada o prístupové ID, kliknite na tlačidlo <b>'Získať ID'</b>. Vaše unikátne ID sa zobrazí v tejto záložke a tiež na hlavnej stránke <b>'Informácie'</b>.</li></ul><p>Všetky stavy (inštalácia, bežiaca služba) sú prehľadne zobrazené pomocou indikátorov na tejto stránke a tiež na karte <b>'Informácie'</b>.</p></body></html>"

    property string lecturerHelpText: "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\"><html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">p, li { white-space: pre-wrap; } h3 { color: #55aaff; margin-bottom: 5px; } h4 { color: #e67e22; margin-bottom: 3px; } ul, ol { padding-left: 20px; } .warning { color: #ffc107; font-weight: bold; }</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\"><p>Vitajte v aplikácii Macrosoft Support. Táto príručka vám pomôže pochopiť a efektívne využívať všetky jej funkcie určené pre lektorov.</p><h3>1. Nahrávanie Online Stretnutí</h3><p>Hlavnou funkciou aplikácie pre lektorov je nahrávanie online stretnutí alebo prednášok. Aplikácia na to využíva softvér <b>OBS Studio</b>, ktorý automatizuje proces nahrávania a ukladania záznamov do databázy.</p><h4>A. Prvotné Nastavenie OBS (Veľmi Dôležité!)</h4><p>Pred prvým nahrávaním je nevyhnutné správne nastaviť OBS. Tento krok stačí urobiť iba raz.</p><ol><li>Prejdite na kartu <b>'Nahrávanie'</b>. Ak OBS nie je nainštalované, použite tlačidlo <b>'Inštalovať OBS'</b>.</li><li>Po inštalácii kliknite na tlačidlo <b>'Otvoriť OBS'</b>.</li><li>V okne OBS nájdite panel <b>'Scény'</b> (zvyčajne vľavo dole). Kliknite na tlačidlo '+' a vytvorte novú scénu (môžete ju pomenovať napr. 'Nahrávanie prednášky').</li><li>Vedľa panelu 'Scény' sa nachádza panel <b>'Zdroje'</b>. Uistite sa, že máte zvolenú novovytvorenú scénu a kliknite na tlačidlo '+'.</li><li>Z ponuky vyberte <b>'Záznam obrazovky'</b> (Screen Capture). V dialógovom okne potvrďte vytvorenie nového zdroja a vyberte monitor, ktorý chcete nahrávať.</li><li>Znova kliknite na '+' v paneli 'Zdroje' a pridajte <b>'Záznam vstupného zvuku'</b> (Audio Input Capture). Vyberte mikrofón, ktorý používate.</li></ol><p class=\"warning\">Bez správne nastavenej scény v OBS sa nahrávka nevytvorí správne (môže byť čierna obrazovka bez zvuku). Naša aplikácia scénu nenastavuje, iba spúšťa a zastavuje streamovanie.</p><h4>B. Postup pri Nahrávaní</h4><ol><li><b>Pred začiatkom</b> online stretnutia sa uistite, že máte spustenú túto podpornú aplikáciu.</li><li>Keď na našej webovej stránke kliknete na tlačidlo pre spustenie nahrávania, táto aplikácia to automaticky rozpozná.</li><li>Aplikácia sama spustí OBS (ak už nebeží) a začne streamovať (nahrávať) do našej databázy. Stav nahrávania môžete sledovať na karte <b>'Nahrávanie'</b>.</li><li><span class=\"warning\">Počas nahrávania NEZATVÁRAJTE ani túto aplikáciu, ani OBS.</span></li><li>Po skončení nahrávania (keď ho ukončíte na webovej stránke) počkajte na potvrdzujúcu správu. Až potom môžete aplikácie bezpečne zavrieť.</li></ol><h3>2. Povolenia pre Kameru a Mikrofón</h3><p>Táto funkcia slúži na udelenie prístupu našej webovej stránke k vašej kamere a mikrofónu. Na karte <b>'Povolenia'</b> použite príslušné tlačidlá na udelenie prístupu.</p><h3>3. Vzdialená Podpora (MacrosoftConnectQuickSupport)</h3><p>Táto funkcia vám umožňuje poskytnúť vzdialenú pomoc klientom. Na karte <b>'Služby'</b> môžete spravovať aplikáciu pre vzdialený prístup, aby ste sa mohli pripojiť k počítaču klienta, keď potrebuje pomoc.</p></body></html>"


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