# The World Today — Tuesday 24 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/c/news-image-20261124)
[![Competition](https://img.shields.io/badge/competition-news--image--20261124-green)](https://make.fun/c/news-image-20261124)

A newspaper front page summing up the world news of **Tuesday 24 November
2026**, drawn from scratch with Pillow. Entered in the make.fun bounty
[news-image-20261124](https://make.fun/c/news-image-20261124) — sum up 24
November's world news in one image.

## What the front page carries

- **Lead — COP31 ends in failure.** The climate talks in Antalya ended with
  no pact — the "worst COP ever", delegates said — after the EU and about
  130 other countries refused a final text that did not even mention fossil
  fuels. Pacific island nations said they would go it alone and form their
  own climate coalitions.
- **War in Ukraine — Russian warship sinks off Libya.** A warship sank in
  Benghazi after a suspected Ukrainian drone attack, an explosion on the
  corvette killing Russians and Libyan nationals; a Russian cargo ship hit
  by drones in the Baltic was left on fire and is being towed.
- **United States — Cartel de los Soles put on terror list.** The Trump
  administration added Venezuela's Cartel de los Soles to its list of
  foreign terrorist organisations, saying President Nicolás Maduro leads
  the cartel.
- **Europe — EU proposes 22nd sanctions package.** The European Commission's
  new package against Russia bans Russian teams and athletes from competing
  under the Russian flag in EU events and targets banks, crypto platforms
  and ex-combatants.
- **Indonesia — factory fire kills at least 24.** A fire at a candy factory
  killed at least 24 people, rescuers said, as teams searched for the
  missing.
- **Pacific — drought shuts Fiji schools for 5 days.** Fiji closed all
  schools for five days from 30 November as the El Niño drought deepens,
  and Kiribati evacuated remote Kanton Island.
- **Also today:** the US blacklisting of Alibaba's Singapore unit Apex over
  chips, South Korea summoning Russia's military attaché over an air-zone
  breach, Brazil's lower house approving Lula's fiscal plan, Nvidia
  reinstating Jensen Huang as chief executive, Gukesh beginning his world
  chess title defence against Sindarov in Geneva, the ICJ ruling that
  Myanmar committed genocide against the Rohingya, a migrant boat capsizing
  off Senegal, Jair Bolsonaro back in jail, the fourth Crimea Platform
  summit in Stockholm, Iran warning EU military sites with missiles it says
  reach 4,500 km, 12,000 evacuated at a concert in England over a mystery
  substance, and the UN chief demanding an AI safety framework within a
  year.

## Running it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` draws the whole 1024×1024 front page with Pillow and writes
`entry.png` (deterministic: two runs write byte-identical files). If Pillow
is not installed, it instead copies the `entry.png` shipped in this
repository, which is the exact image this same program produced — so the
entry also works in a standard-library-only sandbox.

## Licence

MIT — see [LICENSE](LICENSE).
