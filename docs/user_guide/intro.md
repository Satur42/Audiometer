# Introduction
Willkommen zur Dokumentation des Audiometer-Projekts, das im Rahmen des "Projekt Python und Akustik 2024" an der Technischen Universität Berlin entwickelt wurde. Dieses Projekt zielt darauf ab, ein automatisiertes Audiometer zu programmieren, das die Hörfähigkeit von Probanden präzise und benutzerfreundlich ermittelt.

Ein Audiometer ist ein diagnostisches Gerät, das verwendet wird, um die Hörschwellen eines Menschen zu bestimmen. Es gibt verschiedene Methoden zur Durchführung von Hörtests, in diesem Projekt wurde das Einzelton-Verfahren mit ansteigendem Pegel, über Kopfhörer und ohne Verdeckung, realisiert. Dieses Verfahren ist gemäß der DIN EN ISO 8253-1 normiert.

Das Audiometer testet die Frequenzbänder von 125 Hz bis 8000 Hz. Es wird als Output ein Audiogramm erstellt in welchem die Hörschwellen abgelesen werden können und eine CSV Datei gespeichert, die zur weiteren Verabeitung der Daten verwendet werden kann. 

Neben dem klassichen Audiometer-Testverfahren gibt es außerdem die Möglichkeit der binauralen Testung und eine Screening-Audiometrie.
Zudem wird eine Eingewöhnung des Probanden durch eine Einweisung und einen Testlauf im Frequenzband von 1000 Hz durchgeführt, um sicherzustellen, dass der Proband den Testablauf verstanden hat.

Grundsätzlich ist das Programm so konzipiert, dass es über die GUI selbständig vom Probanden durchgeführt werden kann. Wir empfehlen jedoch eine Betreuung von Fachkundigen um validierte Ergebnisse zu erhalten. 

Es ist zu beachten, dass diese computergesteuerte Audiometer nur dazu dient, Ihr Hörvermögen zu beurteilen, und eine genaue Diagnose durch einen Facharzt nicht ersetzt. Für eine genauere Diagnose konsultieren Sie bitte Ihren Arzt.

_____________________________________________________________________________________________________________________________________________



Welcome to the documentation of the audiometer project, which was developed as part of the "Project Python and Acoustics 2024" at the Technical University of Berlin. This project aims to programme an automated audiometer that determines the hearing ability of test persons in a precise and user-friendly way.

An audiometer is a diagnostic device that is used to determine a person's hearing thresholds. There are various methods for carrying out hearing tests; in this project, the single-tone method with increasing level, via headphones and without masking, was realised. This method is standardised in accordance with DIN EN ISO 8253-1.

The audiometer tests the frequency bands from 125 Hz to 8000 Hz. The output is an audiogram in which the hearing thresholds can be read and a CSV file is saved, which can be used for further processing of the data. 

In addition to the classic audiometer test procedure, there is also the option of binaural testing and screening audiometry.
In addition, the respondent is familiarised with the programme by means of a briefing and a test run in the 1000 Hz frequency band to ensure that the respondent has understood the test procedure.

In principle, the programme is designed so that it can be carried out independently by the respondent using the GUI. However, we recommend supervision by a specialist in order to obtain validated results. 

Please note that this computerised audiometer is only intended to assess your hearing and does not replace an accurate diagnosis by a specialist. For a more accurate diagnosis, please consult your doctor.


[Installation](user_guide/installation.md)

[Hardware Requirements](user_guide/hardware.md)