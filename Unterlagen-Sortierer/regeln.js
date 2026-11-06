// =====================================================================
//  Unterlagen-Sortierer – Regeln
//  Diese Datei kann mit dem Editor angepasst werden.
//  Nach dem Speichern das Programm im Browser neu laden (F5).
//
//  Aufbau eines Dokumenttyps:
//    name:   so erscheint der Typ im Dateinamen (ohne Leerzeichen empfohlen)
//    stark:  Begriffe, die den Typ eindeutig kennzeichnen (zählen 3 Punkte)
//    schwach: Begriffe, die oft vorkommen, aber nicht eindeutig sind (1 Punkt)
//  Groß-/Kleinschreibung und Umlaute (ä/ae) spielen keine Rolle.
//  Steht ein Begriff im oberen Teil der ersten Seite (Überschrift),
//  zählt er 1,5-fach.
// =====================================================================

window.REGELN = {

  // Platzhalter: {Nachname} {Vorname} {Dokumenttyp} {Datum} {Original}
  // {Datum} ist das erste im Dokument gefundene Datum (JJJJ-MM-TT).
  dateiname: "{Nachname}_{Vorname}_{Dokumenttyp}",

  // Wie viele Seiten pro Dokument ausgewertet werden (mehr = langsamer)
  seitenProDokument: 2,

  // Typ, wenn nichts passt
  unbekannt: "Sonstiges",

  dokumenttypen: [
    { name: "Antrag",
      stark: ["Antrag auf Grundsicherung", "Antrag auf Leistungen", "Grundsicherung im Alter und bei Erwerbsminderung",
              "Hiermit beantrage ich", "Weiterbewilligungsantrag", "Antrag auf Weiterbewilligung", "Hauptantrag"],
      schwach: ["Antragsteller", "Antragstellerin", "Unterschrift", "SGB XII", "Bedarfsgemeinschaft"] },

    { name: "Kontoauszug",
      stark: ["Kontoauszug", "Alter Kontostand", "Neuer Kontostand", "Kontostand am", "Umsatzanzeige", "Umsatzübersicht"],
      schwach: ["Buchungstag", "Valuta", "Wertstellung", "IBAN", "BIC", "Saldo", "Lastschrift", "Gutschrift", "Überweisung"] },

    { name: "Mietbescheinigung",
      stark: ["Mietbescheinigung", "Vermieterbescheinigung", "Bescheinigung des Vermieters"],
      schwach: ["Vermieter", "Grundmiete", "Wohnfläche"] },

    { name: "Mietvertrag",
      stark: ["Mietvertrag", "Wohnraummietvertrag", "Mietvertrag über Wohnraum", "Mietsache", "Untermietvertrag"],
      schwach: ["Vermieter", "Mieter", "Kaltmiete", "Nettokaltmiete", "Kaution", "Mietbeginn", "Wohnfläche"] },

    { name: "Nebenkostenabrechnung",
      stark: ["Betriebskostenabrechnung", "Nebenkostenabrechnung", "Heizkostenabrechnung", "Heiz- und Betriebskosten"],
      schwach: ["Abrechnungszeitraum", "Nachzahlung", "Guthaben", "Umlageschlüssel", "Vorauszahlungen"] },

    { name: "Energieabrechnung",
      stark: ["Stromrechnung", "Jahresabrechnung Strom", "Gasabrechnung", "Stromabrechnung", "Energieabrechnung"],
      schwach: ["kWh", "Zählerstand", "Abschlag", "Stadtwerke", "Verbrauch"] },

    { name: "Rentenanpassung",
      stark: ["Rentenanpassung", "Mitteilung über die Anpassung", "Anpassung Ihrer Rente"],
      schwach: ["Deutsche Rentenversicherung", "Rente"] },

    { name: "Rentenbescheid",
      stark: ["Rentenbescheid", "Bescheid über Ihre Rente", "Altersrente", "Erwerbsminderungsrente", "Witwenrente", "Witwerrente",
              "Hinterbliebenenrente", "Rentenauskunft", "Betriebsrente"],
      schwach: ["Deutsche Rentenversicherung", "Rentenversicherung", "Rentennummer", "Versicherungsnummer", "Zahlbetrag", "Rente"] },

    { name: "Lohnabrechnung",
      stark: ["Verdienstabrechnung", "Entgeltabrechnung", "Lohnabrechnung", "Gehaltsabrechnung", "Bezügemitteilung"],
      schwach: ["Brutto", "Netto", "Auszahlungsbetrag", "Lohnsteuer", "Sozialversicherung", "Arbeitgeber"] },

    { name: "Ausweis",
      stark: ["Personalausweis", "Identity Card", "Reisepass", "Passport", "Aufenthaltstitel", "Aufenthaltserlaubnis",
              "Niederlassungserlaubnis"],
      schwach: ["Bundesrepublik Deutschland", "Staatsangehörigkeit", "Geburtsort", "Gültig bis"] },

    { name: "Meldebescheinigung",
      stark: ["Meldebescheinigung", "Aufenthaltsbescheinigung", "Anmeldebestätigung", "Bestätigung der Anmeldung"],
      schwach: ["Meldebehörde", "Einwohnermeldeamt", "Bürgeramt", "wohnhaft"] },

    { name: "Krankenversicherung",
      stark: ["Mitgliedsbescheinigung", "Versicherungsbescheinigung", "Krankenversicherungsnachweis", "Mitgliedschaftsbescheinigung"],
      schwach: ["Krankenkasse", "Krankenversicherung", "AOK", "Barmer", "Techniker Krankenkasse", "DAK", "IKK", "BKK", "Beitrag"] },

    { name: "Pflegebescheid",
      stark: ["Pflegegrad", "Pflegebedürftigkeit", "Einstufung in den Pflegegrad"],
      schwach: ["Pflegekasse", "Medizinischer Dienst", "Pflegegeld"] },

    { name: "Schwerbehinderung",
      stark: ["Schwerbehindertenausweis", "Grad der Behinderung", "Feststellungsbescheid", "Merkzeichen"],
      schwach: ["GdB", "Versorgungsamt", "Schwerbehinderung"] },

    { name: "Versicherungsschein",
      stark: ["Versicherungsschein", "Lebensversicherung", "Sterbegeldversicherung", "Rückkaufswert", "Rentenversicherungsvertrag",
              "Haftpflichtversicherung", "Hausratversicherung"],
      schwach: ["Police", "Versicherungsnehmer", "Versicherungsbeginn", "Beitrag", "Versicherungssumme"] },

    { name: "Vermoegensnachweis",
      stark: ["Sparbuch", "Depotauszug", "Bausparvertrag", "Kontostandsbestätigung", "Vermögensaufstellung", "Sparvertrag",
              "Festgeld", "Tagesgeld"],
      schwach: ["Guthaben", "Zinsen", "Sparkasse", "Volksbank"] },

    { name: "Kindergeld",
      stark: ["Familienkasse", "Kindergeld", "Kinderzuschlag"],
      schwach: ["Bundesagentur für Arbeit"] },

    { name: "Unterhalt",
      stark: ["Unterhaltszahlung", "Unterhaltstitel", "Unterhaltsvorschuss", "Unterhaltsvereinbarung"],
      schwach: ["Unterhalt", "Unterhaltspflicht"] },

    { name: "Vollmacht",
      stark: ["Vollmacht", "Betreuerausweis", "Bestellung zum Betreuer", "Betreuungsgericht", "Vorsorgevollmacht"],
      schwach: ["Bevollmächtigte", "Betreuer", "Betreuerin", "Amtsgericht"] },

    { name: "Bescheid",
      stark: ["Rechtsbehelfsbelehrung", "Wohngeldbescheid", "Bewilligungsbescheid", "Ablehnungsbescheid", "Änderungsbescheid"],
      schwach: ["Bescheid", "Widerspruch", "Jobcenter", "Wohngeld", "Landratsamt", "Sozialamt"] },

    { name: "Vertrag",
      stark: ["Vertrag zwischen", "Vertragspartner", "Kaufvertrag", "Darlehensvertrag", "Arbeitsvertrag"],
      schwach: ["Vertrag", "Vertragslaufzeit", "Kündigung"] }
  ]
};
