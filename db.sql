SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Datenbank: `notenas`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `benutzer`
--

CREATE TABLE `benutzer` (
  `id` int(11) NOT NULL,
  `nutzername` varchar(100) DEFAULT NULL,
  `passwort_hash` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `discord` varchar(255) DEFAULT NULL,
  `bestaetigt` tinyint(1) DEFAULT 0,
  `rolle` varchar(10) DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `noten`
--

CREATE TABLE `noten` (
  `id` int(11) NOT NULL,
  `titel` varchar(255) DEFAULT NULL,
  `ordner` varchar(255) DEFAULT NULL,
  `dateiname` varchar(255) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `benutzer_id` int(11) DEFAULT NULL,
  `share_token` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `paypal_payments`
--

CREATE TABLE `paypal_payments` (
  `id` int(11) NOT NULL,
  `payer_name` varchar(255) DEFAULT NULL,
  `payer_email` varchar(255) DEFAULT NULL,
  `payment_id` varchar(255) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `payment_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
