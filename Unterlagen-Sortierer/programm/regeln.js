// =====================================================================
//  Unterlagen-Sortierer – Regeln
//  Diese Datei kann mit dem Editor angepasst werden.
//  Nach dem Speichern das Programm im Browser neu laden (F5).
//
//  Aufbau eines Dokumenttyps:
//    name:   so erscheint der Typ im Dateinamen (Kürzel der Kolleginnen)
//    info:   Erläuterung zum Kürzel (erscheint in der Regeln-Ansicht)
//    stark:  Begriffe, die den Typ eindeutig kennzeichnen (zählen 3 Punkte)
//    schwach: Begriffe, die oft vorkommen, aber nicht eindeutig sind (1 Punkt)
//  Groß-/Kleinschreibung und Umlaute (ä/ae) spielen keine Rolle.
//  Steht ein Begriff im oberen Teil der ersten Seite (Überschrift),
//  zählt er 1,5-fach.
// =====================================================================

window.REGELN = {

  // Platzhalter: {Nachname} {Vorname} {Dokumenttyp} {Datum} {Eingang} {Original}
  // {Datum} ist das erste im Dokument gefundene Datum (JJJJ-MM-TT).
  dateiname: "{Nachname}_{Vorname}_{Dokumenttyp}",

  // Typ, wenn nichts passt
  unbekannt: "Sonstiges",

  // Namen aus dem Dokument erkennen? Standard: false – der Name wird nur oben in der
  // Werkzeugleiste eingetragen ("In markierte Zeilen eintragen"), die Tabelle zeigt
  // keine Namens-Spalten. true = das Programm liest Namen aus den Dokumenten
  // (z. B. wenn Unterlagen mehrerer Personen gemischt eingelesen werden).
  namenErkennen: false,

  // Text vor dem erkannten Dokumenttext, wenn "Mit Prüfauftrag kopieren" gedrückt wird
  // (zum Einfügen in den DSGVO-konformen KI-Assistenten). Leer lassen = Knopf ausblenden.
  pruefauftrag: "Bitte prüfe das folgende Verwaltungsdokument: Um welchen Dokumenttyp handelt es sich? Fehlen Angaben oder Unterschriften, gibt es unplausible oder widersprüchliche Angaben? Welche Rückfragen sollten gestellt werden? Antworte kurz in Stichpunkten.",

  dokumenttypen: [
    // ---------- Anträge (Jobcenter / Sozialamt) ----------
    { name: "HA", info: "Hauptantrag (Jobcenter)",
      stark: ["Hauptantrag", "Antrag auf Leistungen zur Sicherung des Lebensunterhalts"],
      schwach: ["Bürgergeld", "Jobcenter", "SGB II", "Bedarfsgemeinschaft"] },

    { name: "WBA", info: "Weiterbewilligungsantrag",
      stark: ["Weiterbewilligungsantrag", "Antrag auf Weiterbewilligung", "Fortzahlungsantrag"],
      schwach: ["Bewilligungsabschnitt", "Jobcenter"] },

    { name: "Antrag", info: "Antrag Grundsicherung / Sozialhilfe (SGB XII)",
      stark: ["Antrag auf Grundsicherung", "Grundsicherung im Alter und bei Erwerbsminderung",
              "Hiermit beantrage ich"],
      schwach: ["Antragsteller", "Antragstellerin", "Unterschrift", "SGB XII", "Bedarfsgemeinschaft"] },

    { name: "Antrag Erstausstattung", info: "Antrag auf Erstausstattung",
      stark: ["Erstausstattung"],
      schwach: ["Wohnung", "Bekleidung", "Hausrat"] },

    { name: "OAW", info: "Ortsabwesenheit (Antrag / Rückmeldung)",
      stark: ["Ortsabwesenheit", "ortsabwesend"],
      schwach: ["Rückkehr", "Erreichbarkeit", "Urlaub"] },

    // ---------- SGB-II-Anlagen (tragen ihr Kürzel aufgedruckt) ----------
    { name: "EK", info: "Anlage EK – Einkommen",
      stark: ["Anlage EK"], schwach: ["Einkommen"] },

    { name: "EKS", info: "Anlage EKS – Einkommen aus selbständiger Tätigkeit",
      stark: ["Anlage EKS", "Einkommen aus selbständiger Tätigkeit"],
      schwach: ["Betriebseinnahmen", "Betriebsausgaben", "selbständig"] },

    { name: "VM", info: "Anlage VM – Vermögen",
      stark: ["Anlage VM"], schwach: ["Vermögen"] },

    { name: "KDU", info: "Anlage KDU – Kosten der Unterkunft",
      stark: ["Anlage KDU", "Kosten der Unterkunft"],
      schwach: ["Unterkunft und Heizung", "Kaltmiete"] },

    { name: "MEB", info: "Anlage MEB – Mehrbedarf",
      stark: ["Anlage MEB"], schwach: ["Mehrbedarf"] },

    { name: "WEP", info: "Anlage WEP – weitere Person in der Bedarfsgemeinschaft",
      stark: ["Anlage WEP"], schwach: ["weitere Person", "Bedarfsgemeinschaft"] },

    { name: "UH1", info: "Anlage UH1 – Unterhalt",
      stark: ["Anlage UH1"], schwach: ["Unterhalt"] },

    { name: "UH2", info: "Anlage UH2 – Unterhalt",
      stark: ["Anlage UH2"], schwach: ["Unterhalt"] },

    { name: "UH3", info: "Anlage UH3 – Unterhalt",
      stark: ["Anlage UH3"], schwach: ["Unterhalt"] },

    { name: "VÄM", info: "Veränderungsmitteilung",
      stark: ["Veränderungsmitteilung", "Mitteilung über Veränderungen"],
      schwach: ["Änderung der Verhältnisse", "Jobcenter"] },

    { name: "MP", info: "Mitwirkungspflicht",
      stark: ["Mitwirkungspflicht", "fehlende Mitwirkung", "zur Mitwirkung"],
      schwach: ["Mitwirkung", "SGB I", "Frist"] },

    // ---------- Kürzel, deren Bedeutung noch zu klären ist (siehe Hinweis unten) ----------
    { name: "BB",  info: "Kürzel BB – Bedeutung bitte mit den Kolleginnen klären und hier ergänzen",
      stark: ["Anlage BB"], schwach: [] },
    { name: "HG",  info: "Kürzel HG – Bedeutung bitte klären und hier ergänzen",
      stark: ["Anlage HG"], schwach: [] },
    { name: "SE",  info: "Kürzel SE – Bedeutung bitte klären und hier ergänzen",
      stark: ["Anlage SE"], schwach: [] },
    { name: "SV",  info: "Kürzel SV – Bedeutung bitte klären und hier ergänzen",
      stark: ["Anlage SV"], schwach: [] },
    { name: "UF",  info: "Kürzel UF – Bedeutung bitte klären und hier ergänzen",
      stark: ["Anlage UF"], schwach: [] },
    { name: "VE",  info: "Kürzel VE – Bedeutung bitte klären und hier ergänzen",
      stark: ["Anlage VE"], schwach: [] },
    { name: "Nwdigital", info: "Kürzel Nwdigital – Bedeutung bitte klären und hier ergänzen",
      stark: ["Nwdigital"], schwach: [] },
    { name: "Mantelbogen", info: "Mantelbogen – Suchbegriffe bitte bei Bedarf schärfen",
      stark: ["Mantelbogen"], schwach: [] },
    { name: "Profilbogen", info: "Profilbogen – Suchbegriffe bitte bei Bedarf schärfen",
      stark: ["Profilbogen"], schwach: [] },

    // ---------- Einkommen und Konto ----------
    { name: "KTA", info: "Kontoauszug",
      stark: ["Kontoauszug", "Alter Kontostand", "Neuer Kontostand", "Kontostand am", "Umsatzanzeige", "Umsatzübersicht"],
      schwach: ["Buchungstag", "Valuta", "Wertstellung", "IBAN", "BIC", "Saldo", "Lastschrift", "Gutschrift", "Überweisung"] },

    { name: "PayPal-Auszug", info: "PayPal-Kontoauszug",
      stark: ["PayPal"],
      schwach: ["Transaktion", "Händler", "Guthaben"] },

    { name: "LAB", info: "Lohnabrechnung",
      stark: ["Verdienstabrechnung", "Entgeltabrechnung", "Lohnabrechnung", "Gehaltsabrechnung", "Bezügemitteilung"],
      schwach: ["Brutto", "Netto", "Auszahlungsbetrag", "Lohnsteuer", "Sozialversicherung", "Arbeitgeber"] },

    { name: "Einkommensbescheinigung", info: "",
      stark: ["Einkommensbescheinigung", "Verdienstbescheinigung"],
      schwach: ["Einkommen", "Arbeitgeber", "brutto"] },

    { name: "Arbeitsbescheinigung", info: "",
      stark: ["Arbeitsbescheinigung"],
      schwach: ["Arbeitgeber", "Beschäftigungsverhältnis", "beschäftigt"] },

    { name: "AV", info: "Arbeitsvertrag",
      stark: ["Arbeitsvertrag", "Anstellungsvertrag", "Dienstvertrag"],
      schwach: ["Arbeitgeber", "Arbeitnehmer", "Probezeit", "Vergütung", "Arbeitszeit"] },

    { name: "ALG-I", info: "Arbeitslosengeld I",
      stark: ["Arbeitslosengeld"],
      schwach: ["Agentur für Arbeit", "Anspruchsdauer", "Bemessungsentgelt"] },

    { name: "BA", info: "Sonstiges Schreiben der Agentur für Arbeit",
      stark: [],
      schwach: ["Agentur für Arbeit", "Bundesagentur für Arbeit", "Kundennummer"] },

    // ---------- Wohnen ----------
    { name: "MB", info: "Mietbescheinigung",
      stark: ["Mietbescheinigung", "Vermieterbescheinigung", "Bescheinigung des Vermieters"],
      schwach: ["Vermieter", "Grundmiete", "Wohnfläche"] },

    { name: "MV", info: "Mietvertrag",
      stark: ["Mietvertrag", "Wohnraummietvertrag", "Mietvertrag über Wohnraum", "Mietsache", "Untermietvertrag"],
      schwach: ["Vermieter", "Mieter", "Kaltmiete", "Nettokaltmiete", "Kaution", "Mietbeginn", "Wohnfläche"] },

    { name: "NK", info: "Nebenkosten- / Betriebskostenabrechnung",
      stark: ["Betriebskostenabrechnung", "Nebenkostenabrechnung", "Heizkostenabrechnung", "Heiz- und Betriebskosten"],
      schwach: ["Abrechnungszeitraum", "Nachzahlung", "Guthaben", "Umlageschlüssel", "Vorauszahlungen"] },

    { name: "Energieabrechnung", info: "Strom- / Gasabrechnung",
      stark: ["Stromrechnung", "Jahresabrechnung Strom", "Gasabrechnung", "Stromabrechnung", "Energieabrechnung"],
      schwach: ["kWh", "Zählerstand", "Abschlag", "Stadtwerke", "Verbrauch"] },

    { name: "WoGG", info: "Wohngeld",
      stark: ["Wohngeld", "Wohngeldbescheid", "Mietzuschuss", "Lastenzuschuss"],
      schwach: ["Wohngeldstelle", "Wohngeldgesetz"] },

    { name: "Tilgungsplan", info: "Zins- und Tilgungsplan Eigenheim",
      stark: ["Tilgungsplan", "Zins- und Tilgungsplan"],
      schwach: ["Darlehen", "Restschuld", "Annuität"] },

    // ---------- Rente und Versicherung ----------
    { name: "DRV", info: "Deutsche Rentenversicherung (Bescheid, Anpassung, Auskunft)",
      stark: ["Rentenbescheid", "Bescheid über Ihre Rente", "Altersrente", "Erwerbsminderungsrente", "Witwenrente",
              "Witwerrente", "Hinterbliebenenrente", "Rentenauskunft", "Betriebsrente", "Rentenanpassung",
              "Mitteilung über die Anpassung", "Anpassung Ihrer Rente"],
      schwach: ["Deutsche Rentenversicherung", "Rentenversicherung", "Rentennummer", "Versicherungsnummer", "Zahlbetrag", "Rente"] },

    { name: "Rentenversicherungsnummer", info: "Nachweis der Rentenversicherungsnummer",
      stark: ["Versicherungsnummernachweis", "Sozialversicherungsausweis", "Rentenversicherungsnummer"],
      schwach: ["Deutsche Rentenversicherung"] },

    { name: "KV", info: "Krankenversicherung",
      stark: ["Mitgliedsbescheinigung", "Versicherungsbescheinigung", "Krankenversicherungsnachweis", "Mitgliedschaftsbescheinigung"],
      schwach: ["Krankenkasse", "Krankenversicherung", "AOK", "Barmer", "Techniker Krankenkasse", "DAK", "IKK", "BKK", "Beitrag"] },

    { name: "Versicherung", info: "Versicherungsschein / Police",
      stark: ["Versicherungsschein", "Lebensversicherung", "Sterbegeldversicherung", "Rückkaufswert", "Rentenversicherungsvertrag",
              "Haftpflichtversicherung", "Hausratversicherung"],
      schwach: ["Police", "Versicherungsnehmer", "Versicherungsbeginn", "Beitrag", "Versicherungssumme"] },

    { name: "Pflegebescheid", info: "",
      stark: ["Pflegegrad", "Pflegebedürftigkeit", "Einstufung in den Pflegegrad"],
      schwach: ["Pflegekasse", "Medizinischer Dienst", "Pflegegeld"] },

    { name: "Schwerbehinderung", info: "",
      stark: ["Schwerbehindertenausweis", "Grad der Behinderung", "Feststellungsbescheid", "Merkzeichen"],
      schwach: ["GdB", "Versorgungsamt", "Schwerbehinderung"] },

    { name: "Vermögensnachweis", info: "Sparbuch, Depot, Bausparen, Fest-/Tagesgeld",
      stark: ["Sparbuch", "Depotauszug", "Bausparvertrag", "Kontostandsbestätigung", "Vermögensaufstellung", "Sparvertrag",
              "Festgeld", "Tagesgeld"],
      schwach: ["Guthaben", "Zinsen", "Sparkasse", "Volksbank"] },

    // ---------- Familie ----------
    { name: "Kindergeld", info: "",
      stark: ["Kindergeld"],
      schwach: ["Familienkasse", "Bundesagentur für Arbeit"] },

    { name: "KIZ", info: "Kinderzuschlag",
      stark: ["Kinderzuschlag"],
      schwach: ["Familienkasse"] },

    { name: "Elterngeld", info: "",
      stark: ["Elterngeld", "Basiselterngeld", "ElterngeldPlus"],
      schwach: ["Elterngeldstelle", "Elternzeit"] },

    { name: "UH", info: "Unterhalt",
      stark: ["Unterhaltszahlung", "Unterhaltstitel", "Unterhaltsvereinbarung"],
      schwach: ["Unterhalt", "Unterhaltspflicht"] },

    { name: "UHV", info: "Unterhaltsvorschuss",
      stark: ["Unterhaltsvorschuss", "Unterhaltsvorschussgesetz"],
      schwach: ["Jugendamt"] },

    { name: "BuT", info: "Bildung und Teilhabe",
      stark: ["Bildung und Teilhabe", "Bildungspaket", "Teilhabeleistungen"],
      schwach: ["Mittagsverpflegung", "Klassenfahrt", "Schulbedarf", "Lernförderung"] },

    { name: "Geburtsurkunde", info: "",
      stark: ["Geburtsurkunde", "Auszug aus dem Geburtenregister"],
      schwach: ["Standesamt", "geboren am", "Geburtsort"] },

    { name: "Heiratsurkunde", info: "",
      stark: ["Heiratsurkunde", "Eheurkunde", "Auszug aus dem Eheregister"],
      schwach: ["Standesamt", "Eheschließung"] },

    { name: "Scheidungsurteil", info: "",
      stark: ["Scheidungsbeschluss", "wird geschieden", "Ehe der Beteiligten wird"],
      schwach: ["Familiengericht", "Amtsgericht", "Ehesache", "Scheidung"] },

    { name: "Vaterschaftsanerkennung", info: "",
      stark: ["Vaterschaftsanerkennung", "Anerkennung der Vaterschaft"],
      schwach: ["Jugendamt", "beurkundet"] },

    // ---------- Ausweise und Nachweise ----------
    { name: "Ausweis", info: "Personalausweis",
      stark: ["Personalausweis", "Identity Card"],
      schwach: ["Bundesrepublik Deutschland", "Staatsangehörigkeit", "Geburtsort", "Gültig bis"] },

    { name: "Reisepass", info: "",
      stark: ["Reisepass", "Passport"],
      schwach: ["Bundesrepublik Deutschland", "Staatsangehörigkeit"] },

    { name: "AT", info: "Aufenthaltstitel",
      stark: ["Aufenthaltstitel", "Aufenthaltserlaubnis", "Niederlassungserlaubnis"],
      schwach: ["Ausländerbehörde", "befristet", "Gültig bis"] },

    { name: "EMA", info: "Einwohnermeldebescheinigung",
      stark: ["Meldebescheinigung", "Einwohnermeldebescheinigung", "Aufenthaltsbescheinigung", "Anmeldebestätigung", "Bestätigung der Anmeldung"],
      schwach: ["Meldebehörde", "Einwohnermeldeamt", "Bürgeramt", "wohnhaft"] },

    { name: "Führerschein", info: "",
      stark: ["Führerschein", "Fahrerlaubnis", "Driving Licence"],
      schwach: ["Klasse B", "Fahrerlaubnisbehörde"] },

    { name: "KFZ-Schein", info: "Zulassungsbescheinigung",
      stark: ["Zulassungsbescheinigung", "Fahrzeugschein", "Fahrzeugbrief"],
      schwach: ["Kennzeichen", "Erstzulassung", "Halter"] },

    { name: "Steuer-ID", info: "Steuerliche Identifikationsnummer",
      stark: ["Steuerliche Identifikationsnummer", "Steuer-Identifikationsnummer", "Persönliche Identifikationsnummer"],
      schwach: ["Bundeszentralamt für Steuern", "IdNr"] },

    { name: "Schulbescheinigung", info: "",
      stark: ["Schulbescheinigung", "Schulbesuchsbescheinigung"],
      schwach: ["Schule", "Klasse", "Schuljahr", "besucht"] },

    { name: "Studienbescheinigung", info: "Immatrikulationsbescheinigung",
      stark: ["Immatrikulationsbescheinigung", "Studienbescheinigung"],
      schwach: ["Hochschule", "Universität", "Semester", "eingeschrieben", "Matrikelnummer"] },

    { name: "Zeugnis", info: "Schul-, Abschluss- oder Arbeitszeugnis",
      stark: ["Zeugnis"],
      schwach: ["Note", "Leistung", "Verhalten"] },

    { name: "Bewerbung", info: "Bewerbungsunterlagen",
      stark: ["Bewerbung", "Lebenslauf"],
      schwach: ["Anschreiben", "Berufserfahrung", "Kenntnisse"] },

    // ---------- Schreiben und Verfahren ----------
    { name: "Arztbescheinigung", info: "",
      stark: ["Ärztliche Bescheinigung", "Ärztliches Attest", "Ärztliche Stellungnahme", "Arztbrief", "Befundbericht",
              "zur Vorlage beim Träger der Sozialhilfe"],
      schwach: ["Diagnose", "Patient", "Patientin", "Praxis", "Facharzt", "Fachärztin", "ICD", "Krankenkost"] },

    { name: "Kündigung", info: "",
      stark: ["Kündigung", "Kündigungsbestätigung", "kündige ich", "Kündigungsschreiben", "fristlose Kündigung"],
      schwach: ["Kündigungsfrist", "Vertragsende", "zum nächstmöglichen Zeitpunkt", "fristgerecht"] },

    { name: "Mahnung", info: "",
      stark: ["Mahnung", "Zahlungserinnerung", "Mahnbescheid", "letzte Mahnung"],
      schwach: ["offener Betrag", "Mahngebühr", "Zahlungsfrist", "Verzug", "offene Forderung"] },

    { name: "Vollmacht", info: "Vollmacht / Betreuung",
      stark: ["Vollmacht", "Betreuerausweis", "Bestellung zum Betreuer", "Betreuungsgericht", "Vorsorgevollmacht"],
      schwach: ["Bevollmächtigte", "Betreuer", "Betreuerin", "Amtsgericht"] },

    { name: "Widerspruch", info: "",
      stark: ["lege ich Widerspruch", "Widerspruch gegen den Bescheid", "hiermit Widerspruch", "Widerspruchsbescheid"],
      schwach: ["Widerspruch", "Rechtsbehelf", "fristgerecht"] },

    { name: "Stellungnahme", info: "",
      stark: ["Stellungnahme"],
      schwach: ["nehme ich Stellung", "Sachverhalt"] },

    { name: "Erklärung", info: "Schriftliche Erklärung",
      stark: ["Schriftliche Erklärung", "Hiermit erkläre ich", "Eidesstattliche Erklärung", "an Eides statt"],
      schwach: ["erkläre", "versichere"] },

    { name: "Bescheid", info: "Sonstiger Bescheid",
      stark: ["Rechtsbehelfsbelehrung", "Bewilligungsbescheid", "Ablehnungsbescheid", "Änderungsbescheid"],
      schwach: ["Bescheid", "Jobcenter", "Landratsamt", "Sozialamt"] },

    { name: "Vertrag", info: "Sonstiger Vertrag",
      stark: ["Vertrag zwischen", "Vertragspartner", "Kaufvertrag", "Darlehensvertrag"],
      schwach: ["Vertrag", "Vertragslaufzeit", "Kündigung"] }
  ]
};
