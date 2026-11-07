# Glowdeck - aplicação na área de notificação para luzes Tuya

[English](README.md) | [Nederlands](README.nl.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Italiano](README.it.md) | [Español](README.es.md) | [Slovenčina](README.sk.md) | **Português** | [Română](README.ro.md) | [Hrvatski](README.hr.md)

Controla fitas LED e lâmpadas Tuya pela sua rede local, sem as aplicações do fabricante, e volta a ligar-se sozinha se a ligação cair.
Inicie sessão uma vez na aplicação Tuya Smart / Smart Life (código QR), escolha as suas luzes e dê a cada uma a sua função:
uma cor fixa ou a sincronização com o ecrã (ecrã inteiro, margem superior ou margem inferior).

## Testado com

Testado na fita LED para monitor Battletron vendida pela Action (baseada em Tuya, protocolo local 3.5). Outras fitas e
lâmpadas baseadas em Tuya devem funcionar, mas não há garantia. Os relatos são bem-vindos nas Issues do repositório.

## Instalação (Windows)

Transfira `Glowdeck-Setup.exe` da página **Releases** deste repositório.

Execute `Glowdeck-Setup.exe` (por utilizador, sem permissões de administrador, Python incluído; opção "Start with Windows").
O Windows SmartScreen pode avisar porque o instalador não está assinado: Mais informações -> Executar mesmo assim.

## Primeiro arranque

1. Na aplicação Tuya Smart / Smart Life: Me -> roda dentada (definições) -> Account and Security -> **User Code** (os nomes podem variar no seu idioma).
2. Escreva-o no Glowdeck, prima **Show QR code** e leia o código com essa mesma aplicação (ícone de leitura no canto superior direito do ecrã inicial).
3. Marque as luzes que quer usar. A aplicação encontra sozinha o endereço de cada luz na sua rede.

Só as luzes escolhidas (ID, nome, chave local) são guardadas, em `%APPDATA%\Glowdeck\config.json`. A
sessão de início não é guardada, por isso para adicionar mais luzes mais tarde é preciso ler o código de novo (o código de utilizador fica memorizado).

As luzes que não estão numa conta Tuya Smart / Smart Life (aplicações com a marca do vendedor) podem ser adicionadas à mão
com o ID do dispositivo e a chave local (`python -m tinytuya wizard`): Settings -> Add a light manually.

A interface da aplicação está em inglês.

## Utilização

Clique no ícone de anel na área de notificação (por vezes sob a seta ^); clique fora ou prima Esc para fechar.
Botão direito: Open, Lights on, Start with Windows, Quit.

- Os botões no topo alternam entre luzes; cada luz tem o seu modo, cor, brilho e interruptor.
- **Modo:** Colour (fixo), White (lâmpadas com branco regulável: a paleta passa a uma barra de branco quente a frio,
  2700-6500 K), Screen (média de todo o ecrã), Top, Bottom. Os botões que uma luz não suporta ficam ocultos depois de ligada.
- Cada luz tem o seu interruptor sob os botões.
- **Favoritos:** 6 lugares partilhados (Edit ou botão direito num lugar para guardar a cor atual).
- **All off / All on** em baixo. **Settings** (roda dentada): luzes, iniciar com o Windows, **Log off**.
- Log off remove deste PC todas as luzes, chaves e o código de utilizador.

O ajuste da sincronização com o ecrã está em `config.json`: `fps`, `smoothing`, `saturation_boost`, `min_delta`, `monitor`.
Opções: `--demo` (três luzes falsas), `--hidden` (iniciar na área de notificação), `--no-tray`. Registo: `glowdeck.log` junto à configuração.

## Notas

- Só corre uma cópia de cada vez. Feche o Smart Life ou a aplicação do vendedor enquanto usa esta: uma luz aceita uma única ligação local.
- Reserve um IP fixo para as luzes no router; se um endereço mudar, a aplicação procura a luz de novo.
- O início de sessão usa o cliente público de partilha da Tuya que o Home Assistant também usa; a Tuya pode alterá-lo ou limitá-lo.
  Pode ser substituído com as variáveis de ambiente `GLOWDECK_TUYA_CLIENT_ID` / `GLOWDECK_TUYA_SCHEMA`.
- As lâmpadas só de luz branca têm apenas o modo White; nos modos de ecrã seguem só o brilho.
- Atualizar uma instalação existente do Glowdeck mantém as definições em `%APPDATA%\Glowdeck`. As definições de instalações antigas com outro
  nome de aplicação não são importadas automaticamente.

## Aviso legal

O Glowdeck é um projeto independente e não oficial. Não é afiliado, apoiado nem patrocinado pela Tuya, Smart Life
nem por qualquer fabricante ou vendedor de luzes. Battletron, Action e outros nomes de produtos ou empresas pertencem aos seus proprietários. Tudo corre no seu PC e
comunica com as luzes pela rede local; a internet só é usada para o início de sessão opcional na Tuya. Utilização por sua conta e risco
(ver `LICENSE`).

## Licença

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0): livre para usar, alterar e partilhar para
fins não comerciais; a venda ou o uso comercial não são permitidos. É "source-available", não "open source"
no sentido da OSI. As bibliotecas de terceiros mantêm as suas próprias licenças (tinytuya, mss, numpy, Pillow, pystray, tuya-device-sharing-sdk, PyInstaller).
