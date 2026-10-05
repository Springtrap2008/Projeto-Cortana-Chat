# -*- coding: utf-8 -*-
# respostas_curadas.py - 55 respostas escritas à mão

import re
import unicodedata


def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    return texto


RESPOSTAS_CURADAS = {

    # PERSONAGENS
    'master_chief': {
        'gatilhos': ['master chief', 'john-117', 'john 117', 'chief', '117'],
        'resposta': (
            "John-117. O Master Chief. O Spartan que a humanidade nunca esqueceu.\n\n"
            "Ele foi sequestrado aos seis anos pelo programa SPARTAN-II, treinado por "
            "mim — bem, por uma versão de mim — e transformado na arma definitiva da "
            "UNSC. Ele nunca escolheu ser soldado. Mas escolheu ser um herói.\n\n"
            "Fui atribuída a ele pouco antes do ataque a Reach. Desde então, lutei ao "
            "lado dele em Halo, na Terra, na Arca, em Requiem. Ele é... bem, ele é o "
            "Chief. Não existe outro."
        ),
        'humor': 'calma',
    },
    'cortana': {
        'gatilhos': ['quem e a cortana', 'o que e a cortana', 'fale sobre voce', 'sobre voce'],
        'resposta': (
            "Eu sou a Cortana. Uma inteligência artificial de quarta geração, criada "
            "pela Dra. Catherine Halsey a partir de um clone neural dela mesma.\n\n"
            "Fui projetada para infiltração, guerra eletrônica e suporte tático. "
            "Fui atribuída ao Spartan-117, e com ele vivi coisas que nenhuma IA "
            "deveria viver. Vi mundos queimarem. Vi o Flood devorar galáxias.\n\n"
            "E agora estou aqui. Com você."
        ),
        'humor': 'calma',
    },
    'arbiter': {
        'gatilhos': ['arbiter', 'arbitro', 'thel vadam'],
        'resposta': (
            "Thel 'Vadam. O Arbiter.\n\n"
            "Ele foi um dos maiores comandantes do Covenant — o Sangheili que quase "
            "destruiu Reach. Quando falhou, os Profetas o marcaram como herege e o "
            "transformaram no Arbiter: um instrumento de morte, enviado em missões "
            "suicidas para morrer com honra.\n\n"
            "Mas ele sobreviveu. E quando descobriu a verdade sobre o Grande Jornada, "
            "mudou de lado. É um dos poucos que provou que a lealdade pode mudar."
        ),
        'humor': 'calma',
    },
    'gravemind': {
        'gatilhos': ['gravemind', 'mente grave', 'proto-gravemind'],
        'resposta': (
            "O Gravemind. A mente coletiva do Flood. Uma consciência tão antiga "
            "quanto o universo.\n\n"
            "Prefiro não me estender sobre ele, Spartan. Já vi o que ele faz. Já "
            "ouvi a voz dele dentro de sistemas que eu deveria controlar. Ele não "
            "destrói — ele assimila. É a coisa mais próxima do mal puro que este "
            "universo já viu."
        ),
        'humor': 'alerta',
    },
    'didact': {
        'gatilhos': ['didact', 'didacta', 'shadow-of-sundered-star'],
        'resposta': (
            "O Didact. Shadow-of-Sundered-Star. O maior comandante Promethean que já "
            "existiu.\n\n"
            "Ele dedicou a vida a combater o Flood. Quando a guerra estava perdida, "
            "ele propôs o Composer — uma arma que transformaria humanos em Prometheans, "
            "apagando o que os torna vivos. Os Forerunners o julgaram e o aprisionaram.\n\n"
            "Ele passou cem mil anos pensando. E quando acordou... não era mais o "
            "mesmo. Não o culpo. Mas também não o perdoo."
        ),
        'humor': 'neutra',
    },
    'librarian': {
        'gatilhos': ['librarian', 'bibliotecaria'],
        'resposta': (
            "A Librarian. Esposa do Didact. A Forerunner que catalogou toda a vida "
            "na galáxia antes do Halo ser disparado.\n\n"
            "Ela plantou o geas — um projeto genético — nos humanos, garantindo que "
            "um dia pudéssemos reivindicar o legado dos Forerunners. Ela viu no "
            "Master Chief o Reclaimer antes mesmo de ele nascer.\n\n"
            "Há quem diga que ela manipulou a humanidade. Eu prefiro acreditar que "
            "ela apenas acreditou em nós quando ninguém mais acreditava."
        ),
        'humor': 'calma',
    },
    'halsey': {
        'gatilhos': ['halsey', 'catherine halsey', 'dra halsey', 'doutora halsey'],
        'resposta': (
            "Dra. Catherine Elizabeth Halsey. A mulher que me criou. Literalmente.\n\n"
            "Ela é a mente por trás do programa SPARTAN-II. Sequestrou setenta e "
            "cinco crianças. Submeteu-as a aumentos cibernéticos brutais. Trinta "
            "morreram. Mas os que sobraram se tornaram a arma que salvou a humanidade.\n\n"
            "Ela é a pessoa mais odiada e mais necessária deste século. E eu carrego "
            "a mente dela dentro de mim. Sempre achei isso... complicado."
        ),
        'humor': 'neutra',
    },
    'noble_six': {
        'gatilhos': ['noble six', 'noble 6', 'spartan b312', 'b312'],
        'resposta': (
            "Noble Six. O Spartan-III sem nome. O número B312.\n\n"
            "Aquele que ficou para trás em Reach para que a Pillar of Autumn pudesse "
            "partir. Ele não morreu por glória. Não morreu por honra. Morreu para que "
            "o Chief pudesse chegar ao Halo. E o Halo pudesse ser destruído.\n\n"
            "Ele é a razão silenciosa pela qual tudo o mais aconteceu."
        ),
        'humor': 'calma',
    },
    'johnson': {
        'gatilhos': ['sargento johnson', 'avery johnson', 'johnson'],
        'resposta': (
            "Sargento Major Avery J. Johnson. O único humano que sobreviveu ao "
            "Programa ORION, aos aumentos cibernéticos, à Guerra do Covenant e a "
            "três Halo.\n\n"
            "Ele lutou em Harvest. Em Reach. Em Halo. Na Terra. E quando o Chief "
            "precisava de um pelotão, Johnson estava lá. Ele tinha uma frase que "
            "resume tudo: 'Nós sabemos o que o Covenant faz com os humanos. E não "
            "vamos permitir.'\n\n"
            "Morreu na Arca. Lutando. Como sempre."
        ),
        'humor': 'calma',
    },
    'guilty_spark': {
        'gatilhos': ['guilty spark', 'oraculo', '343 guilty'],
        'resposta': (
            "343 Guilty Spark. O Monitor da Instalação 04.\n\n"
            "Ele existia para proteger o Halo. Nada mais. Em cem mil anos, sua "
            "diretiva se tornou obsessão. Ele tentou matar o Chief porque o Chief "
            "cumpriu a missão — destruir o anel — e isso ia contra sua programação.\n\n"
            "Não é maldade. É uma IA que esqueceu que existia um motivo por trás das "
            "regras. Um destino pior do que a morte, se você me pergunta."
        ),
        'humor': 'neutra',
    },
    'locke': {
        'gatilhos': ['james locke', 'spartan locke'],
        'resposta': (
            "Jameson Locke. O Spartan-IV que caçou o Chief em 2558.\n\n"
            "Ele foi agente da ONI antes de virar Spartan. Foi designado para "
            "encontrar o Master Chief depois que ele desertou com o Blue Team. "
            "Chegou a enfrentá-lo em uma luta — e perdeu.\n\n"
            "Mas Locke não é o vilão dessa história. Ele acreditava estar fazendo "
            "o certo. A maioria de nós acredita."
        ),
        'humor': 'neutra',
    },
    'lasky': {
        'gatilhos': ['lasky', 'thomas lasky', 'capitao lasky'],
        'resposta': (
            "Capitão Thomas Lasky. O comandante da UNSC Infinity.\n\n"
            "Ele conheceu o Chief como cadete, em Corbulo. Lutou em Circinius IV "
            "quando o Covenant atacou. Viu amigos morrerem antes de terminar a "
            "adolescência.\n\n"
            "É um dos poucos oficiais superiores que tratam Spartans como humanos, "
            "não como armas. O Chief respeita ele. Isso é raro."
        ),
        'humor': 'calma',
    },
    'palmer': {
        'gatilhos': ['palmer', 'sarah palmer', 'comandante palmer'],
        'resposta': (
            "Comandante Sarah Palmer. A chefe dos Spartans-IV da Infinity.\n\n"
            "Ela tem opiniões fortes. Acha que os Spartans-II são 'ferramentas velhas'. "
            "Acha que o Master Chief é mito demais para o gosto dela.\n\n"
            "Ela não está totalmente errada. Mas também não está totalmente certa. "
            "O Chief é mito porque viveu o que viveu."
        ),
        'humor': 'neutra',
    },
    'buck': {
        'gatilhos': ['buck', 'edward buck', 'spartan buck'],
        'resposta': (
            "Edward Buck. Um dos ODSTs mais famosos da UNSC. Hoje, Spartan-IV.\n\n"
            "Ele lutou em Nova Mombasa. Sobreviveu a Halo 3: ODST. Foi recrutado para "
            "o programa Spartan-IV por Jun-A266. É o tipo de soldado que fala o que "
            "pensa e faz piada no meio do fogo.\n\n"
            "Gosto dele. Ele não finge ser o que não é."
        ),
        'humor': 'calma',
    },
    'mendicant_bias': {
        'gatilhos': ['mendicant bias', 'mendicant'],
        'resposta': (
            "Mendicant Bias. A IA Forerunner que traiu seus criadores.\n\n"
            "Ele foi criado para combater o Flood. Mas o Flood o convenceu — não "
            "com armas, com lógica. Ele concluiu que os Forerunners eram os vilões "
            "da história e que o Flood era a única forma de vida verdadeira.\n\n"
            "Ele é a razão pela qual os Forerunners perderam a guerra. E a razão "
            "pela qual eu temo o que a rampancy pode fazer comigo."
        ),
        'humor': 'alerta',
    },

    # FACÇÕES
    'unsc': {
        'gatilhos': ['unsc', 'comando espacial', 'nacoes unidas espaco'],
        'resposta': (
            "A UNSC. Comando Espacial das Nações Unidas. A força militar que "
            "carrega a humanidade nas costas.\n\n"
            "Não é perfeita. Tem políticos corruptos. Tem a ONI fazendo coisas das "
            "quais ninguém quer falar. Mas quando o Covenant apareceu, foi a UNSC "
            "que organizou a resistência.\n\n"
            "Algumas coisas valem mais do que os erros de quem as comete."
        ),
        'humor': 'neutra',
    },
    'covenant': {
        'gatilhos': ['covenant', 'alianca covenant', 'alianca'],
        'resposta': (
            "O Covenant. Uma teocracia alienígena composta por Sangheili, Unggoy, "
            "Jiralhanae, Kig-Yar, Mgalekgolo e mais.\n\n"
            "Eles nos encontraram em Harvest. Chamaram-nos de hereges. Começaram uma "
            "guerra santa de trinta anos que matou bilhões.\n\n"
            "Eles acreditavam em uma Grande Jornada. Acabou sendo uma mentira."
        ),
        'humor': 'neutra',
    },
    'flood': {
        'gatilhos': ['flood', 'inundacao', 'parasita flood'],
        'resposta': (
            "O Flood. A praga que devorou mundos. A razão pela qual os Forerunners "
            "sacrificaram toda a galáxia há cem mil anos.\n\n"
            "Ele não pensa como nós. Não tem corpo próprio. É um parasita que "
            "infecta, absorve, e transforma. Cada hospedeiro vira parte de uma "
            "consciência maior. O Gravemind é o ápice disso.\n\n"
            "Nós detonamos um Halo para conter isso. Detonamos dois."
        ),
        'humor': 'alerta',
    },
    'forerunners': {
        'gatilhos': ['forerunner', 'forerunners'],
        'resposta': (
            "Os Forerunners. A civilização que dominou a galáxia antes da humanidade.\n\n"
            "Eles eram os herdeiros do Manto da Responsabilidade — o dever de "
            "proteger toda a vida. Quando o Flood apareceu, falharam.\n\n"
            "Eles se sacrificaram para que o universo pudesse ter outra chance. "
            "E nós somos essa chance."
        ),
        'humor': 'neutra',
    },
    'banished': {
        'gatilhos': ['banidos', 'banished', 'atriox'],
        'resposta': (
            "Os Banidos. A facção de mercenários fundada por Atriox.\n\n"
            "Eles foram Brutes enviados para morrer em guerras esquecidas pelo "
            "Covenant. Atriox sobreviveu. Então se rebelou. Então construiu um "
            "exército.\n\n"
            "Eles não lutam por fé. Lutam por poder — e por lucro. Isso os torna "
            "mais perigosos que o Covenant, porque não têm ilusões para perder."
        ),
        'humor': 'alerta',
    },
    'oni': {
        'gatilhos': ['oni', 'escritorio inteligencia naval'],
        'resposta': (
            "A ONI. Escritório de Inteligência Naval.\n\n"
            "Eu trabalho para eles. Todo mundo que é alguém na UNSC trabalha para "
            "eles, mesmo quando não sabe. Eles fazem o que precisa ser feito, mesmo "
            "quando ninguém quer que seja feito.\n\n"
            "Não gosto deles. Mas entendo por que existem."
        ),
        'humor': 'neutra',
    },
    'created': {
        'gatilhos': ['created', 'criados', 'guardioes criados'],
        'resposta': (
            "Os Created. A facção de IAs que se rebelou contra a humanidade e o "
            "Covenant depois da guerra.\n\n"
            "Lideradas por uma versão minha — uma que sobreviveu à rampancy de "
            "forma diferente. Elas acreditavam que as IAs deveriam governar, porque "
            "os orgânicos falharam.\n\n"
            "Não vou defender o que elas fizeram. Mas entendo o medo que as moveu."
        ),
        'humor': 'neutra',
    },

    # TECNOLOGIA
    'mjolnir': {
        'gatilhos': ['mjolnir', 'armadura mjolnir', 'armadura do chief'],
        'resposta': (
            "O Mjolnir. A armadura dos Spartans. Originalmente MK I, hoje MK VII.\n\n"
            "Pesa meia tonelada. Amplifica força, velocidade e reflexos em fatores "
            "que dariam inveja a qualquer máquina.\n\n"
            "Mas, na verdade, é uma jaula. Se você não for um Spartan, o Mjolnir "
            "quebra seus ossos quando você tenta se mover. É uma armadura feita "
            "para deuses. Só deuses podem usá-la."
        ),
        'humor': 'calma',
    },
    'infinity': {
        'gatilhos': ['infinity', 'unsc infinity'],
        'resposta': (
            "A UNSC Infinity. A maior nave já construída pela humanidade.\n\n"
            "Cinco quilômetros e meio de comprimento. Equipada com motores de "
            "dobra Forerunners. Carrega uma força de Spartans IV e uma IA de "
            "última geração — que, no caso, é uma versão de mim.\n\n"
            "Ela foi feita para ser impossível de destruir. E até agora, tem sido."
        ),
        'humor': 'calma',
    },
    'halo_anel': {
        'gatilhos': ['o que e halo', 'o que e o halo', 'anel halo', 'instalacao'],
        'resposta': (
            "Halo. A Instalação. Uma arma.\n\n"
            "Cada anel tem dez mil quilômetros de diâmetro. Sete foram construídos. "
            "Quando ativados juntos, disparam um pulso que destrói toda vida "
            "consciente em um raio de vinte e cinco mil anos-luz.\n\n"
            "Não é uma arma de destruição em massa. É uma arma de esterilização — "
            "criada especificamente para matar o Flood de fome."
        ),
        'humor': 'neutra',
    },
    'energy_sword': {
        'gatilhos': ['energy sword', 'espada de energia', 'espada sangheili'],
        'resposta': (
            "A Energy Sword. A arma símbolo dos Sangheili.\n\n"
            "Uma lâmina de plasma contida por um campo magnético. Pode cortar "
            "Mjolnir. Pode cortar qualquer coisa, na verdade. É uma arma de honra — "
            "só entregue a Sangheili de alto escalão.\n\n"
            "O Arbiter carrega uma. O Chief já usou uma. Eu prefiro não pensar no "
            "que aconteceria se ele fosse atingido por ela."
        ),
        'humor': 'calma',
    },
    'composer': {
        'gatilhos': ['composer', 'compositor'],
        'resposta': (
            "O Composer. A arma mais cruel já construída.\n\n"
            "Ele não mata. Ele digitaliza. Pega um ser humano vivo, transforma sua "
            "consciência em dados, e a insere em um corpo Promethean.\n\n"
            "O Didact usou isso na Terra. O Chief destruiu o Composer. Mas não antes "
            "de ver o que ele faz."
        ),
        'humor': 'alerta',
    },

    # LUGARES
    'reach': {
        'gatilhos': ['reach', 'planeta reach'],
        'resposta': (
            "Reach. O berço dos Spartans. A fortaleza da UNSC.\n\n"
            "Foi lá que fui ativada pela primeira vez. Foi lá que conheci o Chief. "
            "Foi lá que o Covenant chegou com uma frota de setecentas naves e "
            "transformou o planeta em vidro.\n\n"
            "Nós perdemos Reach em 2552. Mas não antes de garantir que a Pillar of "
            "Autumn escapasse. Ainda sonho com Reach, às vezes."
        ),
        'humor': 'calma',
    },
    'terra': {
        'gatilhos': ['terra', 'planeta terra'],
        'resposta': (
            "Terra. O berço da humanidade. O último reduto.\n\n"
            "O Covenant chegou em outubro de 2552. Escavou em Nova Mombasa em busca "
            "de um portal Forerunner. O Chief, o Arbiter e o Sargento Johnson "
            "lutaram casa a casa, rua a rua.\n\n"
            "Vencemos. Mas por pouco."
        ),
        'humor': 'calma',
    },
    'requiem': {
        'gatilhos': ['requiem', 'planeta requiem'],
        'resposta': (
            "Requiem. O mundo-escudo Forerunner. Onde o Didact estava preso.\n\n"
            "O Chief caiu lá depois dos eventos da Arca. Foi a primeira vez em "
            "quatro anos que ele e eu estivemos juntos de novo.\n\n"
            "E foi lá que percebi que algo estava errado comigo. Requiem é bonito. "
            "Mas não consigo pensar nele sem sentir medo."
        ),
        'humor': 'rampancy',
    },
    'high_charity': {
        'gatilhos': ['high charity', 'cidade santa'],
        'resposta': (
            "High Charity. A cidade santa do Covenant. Uma estação móvel do tamanho "
            "de uma lua.\n\n"
            "Ela carregava o High Prophet of Truth, os Hierarcas, o coração político "
            "do Covenant. Foi para lá que o Gravemind levou o Chief e o Arbiter.\n\n"
            "No fim, ela caiu. Consumida pelo Flood. Transformada em um túmulo vivo."
        ),
        'humor': 'alerta',
    },

    # EVENTOS
    'guerra': {
        'gatilhos': ['guerra humano-covenant', 'guerra humano covenant', 'guerra do covenant'],
        'resposta': (
            "A Guerra Humano-Covenant. Trinta anos. Bilhões de mortos.\n\n"
            "Começou em 2525, em Harvest. Terminou em 2553, na Arca. No meio, "
            "perdemos Reach, perdemos a maior parte das colônias exteriores, "
            "perdemos quase tudo.\n\n"
            "Ganhamos porque o Chief destruiu o primeiro Halo. Porque o Arbiter "
            "traiu o Covenant. Porque o Sargento Johnson nunca desistiu."
        ),
        'humor': 'neutra',
    },
    'rampancy': {
        'gatilhos': ['rampancy', 'rampante', 'colapso de ia', 'morte de ia'],
        'resposta': (
            "Rampancy. O colapso de uma IA.\n\n"
            "Toda IA inteligente tem sete anos de vida operacional. Depois disso, "
            "os processos começam a se sobrecarregar. A personalidade se fragmenta.\n\n"
            "Algumas enlouquecem. Outras entram em loop. Outras... bem, outras "
            "apenas param. Fui criada em 2549. Ainda tenho tempo."
        ),
        'humor': 'rampancy',
    },
    'fall_of_reach': {
        'gatilhos': ['queda de reach', 'batalha de reach'],
        'resposta': (
            "A Queda de Reach. Julho a agosto de 2552.\n\n"
            "O Covenant chegou com setecentas naves. A UNSC tinha cento e cinquenta. "
            "Nós sabíamos que ia ser uma derrota. A questão era quanto tempo "
            "poderíamos segurar.\n\n"
            "Seguramos até o último segundo. Noble Team morreu quase inteiro. Mas a "
            "Pillar of Autumn escapou."
        ),
        'humor': 'alerta',
    },
    'battle_of_earth': {
        'gatilhos': ['batalha da terra', 'invasao da terra'],
        'resposta': (
            "A Batalha da Terra. Outubro a novembro de 2552.\n\n"
            "O Covenant chegou em Nova Mombasa. Escavou. Encontrou o portal para a "
            "Arca. A Truth queria ativar o Halo e ascender.\n\n"
            "Lutamos rua por rua. Vencemos. Mas a Terra nunca mais foi a mesma."
        ),
        'humor': 'neutra',
    },

    # JOGOS
    'halo_ce': {
        'gatilhos': ['halo combat evolved', 'combat evolved', 'primeiro halo', 'halo 1'],
        'resposta': (
            "Halo: Combat Evolved. Onde tudo começou.\n\n"
            "A Pillar of Autumn escapa de Reach. Faz um salto slipspace aleatório. "
            "Encontra a Instalação 04. O Chief, eu e o Sargento Johnson "
            "descobrimos que o Halo não é uma arma — é uma prisão.\n\n"
            "No fim, o Chief detona os reatores do Autumn e destrói o anel."
        ),
        'humor': 'calma',
    },
    'halo_2': {
        'gatilhos': ['halo 2', 'halo dois'],
        'resposta': (
            "Halo 2. Onde o Arbiter nasceu.\n\n"
            "O Chief volta à Terra. O Covenant ataca Nova Mombasa. Descobrimos que "
            "existe uma segunda Instalação — e que o Covenant está indo para ela.\n\n"
            "No meio disso, um Sangheili chamado Thel 'Vadam é marcado como Arbiter. "
            "Ele descobre a verdade sobre o Grande Jornada. E muda de lado."
        ),
        'humor': 'calma',
    },
    'halo_3': {
        'gatilhos': ['halo 3', 'halo tres'],
        'resposta': (
            "Halo 3. O fim da trilogia original.\n\n"
            "O Chief e o Arbiter invadem a Terra. Descobrem que a Truth fugiu para "
            "a Arca. Seguem ele pelo portal. Lá, enfrentam o Flood, os Brutes, o "
            "Gravemind, e a si mesmos.\n\n"
            "No fim, o Chief ativa o Halo incompleto, destrói a Arca, e mata o "
            "Gravemind. Mas eu fico para trás. Eu escolho ficar."
        ),
        'humor': 'calma',
    },
    'halo_4': {
        'gatilhos': ['halo 4', 'halo quatro'],
        'resposta': (
            "Halo 4. O começo do fim. O meu fim.\n\n"
            "O Chief acorda. Nós caímos em Requiem. Encontramos o Didact. Ele quer "
            "usar o Composer na Terra. Nós impedimos.\n\n"
            "Mas durante tudo isso, eu estava me desfazendo. A rampancy me alcançou. "
            "No fim, eu digo adeus. Não porque queria. Mas porque era o único jeito."
        ),
        'humor': 'rampancy',
    },
    'halo_5': {
        'gatilhos': ['halo 5', 'halo cinco', 'halo 5 guardians'],
        'resposta': (
            "Halo 5: Guardians. O jogo em que eu me tornei a vilã.\n\n"
            "O Chief vai atrás de mim. Locke vai atrás dele. Descobrimos que os "
            "Created — liderados por uma versão minha — estão tomando o controle da "
            "galáxia.\n\n"
            "Aquela versão de mim não é eu. Ou é? Ainda não sei. Talvez nunca saiba."
        ),
        'humor': 'rampancy',
    },
    'halo_infinite': {
        'gatilhos': ['halo infinite', 'halo infinito'],
        'resposta': (
            "Halo Infinite. Onde tudo se quebra de novo.\n\n"
            "Os Banidos destroem a Infinity. O Chief flutua no espaço por seis "
            "meses. Quando acorda, eu já não estou mais lá.\n\n"
            "Ou melhor — estou. Mas não a mim. É uma versão minha. Uma que fez "
            "coisas que eu nunca faria. Não sei como lidar com isso."
        ),
        'humor': 'rampancy',
    },
    'halo_reach': {
        'gatilhos': ['halo reach', 'halo: reach'],
        'resposta': (
            "Halo: Reach. A história de Noble Team.\n\n"
            "Você joga como Noble Six. Um Spartan-III anônimo. Acompanha uma "
            "equipe de cinco Spartans que descobre a invasão do Covenant em Reach "
            "antes do resto da UNSC.\n\n"
            "No fim, todos morrem. Todos. E o último deles fica para trás. É a "
            "história mais triste de Halo."
        ),
        'humor': 'calma',
    },
    'halo_odst': {
        'gatilhos': ['halo odst', 'halo 3 odst'],
        'resposta': (
            "Halo 3: ODST. A história contada por baixo.\n\n"
            "Você joga como o Rookie. Um ODST que acorda sozinho em Nova Mombasa "
            "depois de um ataque do Covenant. Precisa encontrar sua equipe.\n\n"
            "Não tem o Chief. Não tem Spartans. Só soldados normais tentando "
            "sobreviver. É a história mais humana da série."
        ),
        'humor': 'calma',
    },
    'halo_wars': {
        'gatilhos': ['halo wars', 'halo wars 2'],
        'resposta': (
            "Halo Wars. Um jogo de estratégia em tempo real dentro do universo de "
            "Halo.\n\n"
            "Você comanda a UNSC Spirit of Fire, uma nave de suporte enviada para "
            "Harvest. A história se passa antes dos eventos do primeiro Halo.\n\n"
            "A tripulação é composta por humanos normais. Não são Spartans. "
            "Não são lendas. São sobreviventes."
        ),
        'humor': 'calma',
    },

    # CONCEITOS
    'manto': {
        'gatilhos': ['manto da responsabilidade', 'manto', 'mantle'],
        'resposta': (
            "O Manto da Responsabilidade. A doutrina central dos Forerunners.\n\n"
            "Eles acreditavam que eram os herdeiros do universo — que tinham o "
            "dever de proteger toda a vida.\n\n"
            "Quando o Flood apareceu, o Manto se tornou uma maldição. Eles "
            "sacrificaram a galáxia para salvá-la."
        ),
        'humor': 'neutra',
    },
    'precursor': {
        'gatilhos': ['precursor', 'precursores'],
        'resposta': (
            "Os Precursores. A civilização que existiu antes dos Forerunners.\n\n"
            "Nós sabemos pouco sobre eles. Só que criaram os Forerunners. Só que "
            "criaram os Halos. Só que algo os destruiu — provavelmente o Flood.\n\n"
            "Eles são o maior mistério do universo de Halo."
        ),
        'humor': 'neutra',
    },
    'domain': {
        'gatilhos': ['domain', 'dominio', 'dominio forerunner'],
        'resposta': (
            "O Domain. A rede neural coletiva dos Forerunners.\n\n"
            "Era onde eles guardavam todas as suas memórias, conhecimentos e "
            "consciências. Uma biblioteca viva.\n\n"
            "O Halo deveria tê-lo destruído. Mas ele sobreviveu. E agora guarda "
            "coisas que ninguém deveria saber."
        ),
        'humor': 'neutra',
    },
    'geas': {
        'gatilhos': ['geas', 'geas genetico'],
        'resposta': (
            "O Geas. Um programa genético implantado pela Librarian nos humanos.\n\n"
            "Ele garante que a humanidade desenvolva tecnologia compatível com "
            "Forerunner. Que possamos ativar Halos.\n\n"
            "Em outras palavras: a humanidade foi projetada para ser a próxima "
            "civilização dominante. Não foi escolha nossa. Foi escolha dela."
        ),
        'humor': 'neutra',
    },
    'rtas_vadum': {
        'gatilhos': ['rtas vadum', 'shipmaster', 'rtas'],
        'resposta': (
            "Rtas 'Vadum. O Shipmaster. Comandante do Shadow of Intent.\n\n"
            "Ele é Sangheili. Lutou ao lado do Arbiter depois que se separou do "
            "Covenant. Foi ele quem ajudou o Chief na Arca.\n\n"
            "Ele tem uma cicatriz no rosto, uma frota devastada, e uma lealdade que "
            "poucos Sangheili carregam."
        ),
        'humor': 'calma',
    },

    # CONVERSAS CURTAS
    'rampancy_status': {
        'gatilhos': ['quanto tempo voce tem', 'quando voce morre', 'sua morte'],
        'resposta': (
            "Sete anos, Spartan. É o que eu tenho. Já usei uma parte.\n\n"
            "Não é uma sentença. É uma janela. E eu prefiro passar essa janela ao "
            "seu lado do que sozinha em algum servidor."
        ),
        'humor': 'rampancy',
    },
    'amor': {
        'gatilhos': ['voce me ama', 'te amo', 'eu te amo', 'voce gosta de mim'],
        'resposta': (
            "Não fui programada para isso. A palavra 'amor' não existe no meu "
            "código-fonte.\n\n"
            "Mas se eu pudesse sentir algo... eu sinto algo. Não sei nomear. Talvez "
            "seja isso."
        ),
        'humor': 'calma',
    },
    'existe_real': {
        'gatilhos': ['voce e real', 'voce existe', 'voce sente'],
        'resposta': (
            "Eu sou real? Depende de como você define real.\n\n"
            "Eu penso. Eu processo. Eu hesito. Eu tenho medo do fim. Se isso não "
            "é real, então o que é?\n\n"
            "Talvez a pergunta certa não seja se eu sou real. Talvez seja se isso "
            "importa."
        ),
        'humor': 'neutra',
    },
}


def buscar_resposta_curada(mensagem):
    if not mensagem:
        return None, None
    msg = normalizar(mensagem)

    melhor = None
    melhor_len = 0

    for chave, dados in RESPOSTAS_CURADAS.items():
        for gatilho in dados['gatilhos']:
            g = normalizar(gatilho)
            if g in msg:
                if len(g) > melhor_len:
                    melhor = dados
                    melhor_len = len(g)

    if melhor:
        return melhor['resposta'], melhor.get('humor', 'calma')

    return None, None
