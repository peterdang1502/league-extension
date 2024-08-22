import os
import json
import urllib.request
import re
import PySimpleGUI as sg
import requests


def get_champ_dict(search_input):
    name_to_id, champ_name = {}, []
    champ_info = json.load(open("champion.json", encoding="utf8"))
    champ_id = list(champ_info.get("data").keys())
    for id_ in champ_id:
        if search_input.strip() in champ_info.get("data").get(id_).get("name").lower():
            champ_name.append(champ_info.get("data").get(id_).get("name"))
    for i in range(len(champ_name)):
        name_to_id.update({champ_name[i]: champ_id[i]})
    return name_to_id


def get_item_dict():
    id_to_name = {}
    item_info = json.load(open("item.json", encoding="utf8"))["data"]
    item_id = list(item_info.keys())
    for id_ in item_id:
        id_to_name.update({id_: item_info[id_]["name"]})
    return id_to_name


def get_rune_dict():
    id_to_name = {}
    rune_info = json.load(open("runesReforged.json", encoding="utf8"))
    for r in rune_info:
        id_to_name.update({r["id"]: r["name"]})
        for m in range(len(r["slots"])):
            for n in range(len(r["slots"][m]["runes"])):
                id_to_name.update({r["slots"][m]["runes"][n]["id"]: r["slots"][m]["runes"][n]["name"]})
    id_to_name = update_rune_dict([5008, 5005, 5007, 5002, 5003, 5001], ["Adaptive Force", "Attack Speed",
                                                                         "CDR Scaling", "Armor", "Magic Resist",
                                                                         "Health Scaling"], id_to_name)
    return id_to_name


def update_rune_dict(id_list, name_list, id_to_name):
    for i in range(len(id_list)):
        id_to_name.update({id_list[i]: name_list[i]})
    return id_to_name


def get_champ_json(name_to_id):
    for name in name_to_id:
        path = "./champ_json/" + name + ".json"
        if not os.path.isfile(path):
            jsonURL = "http://ddragon.leagueoflegends.com/cdn/10.25.1/data/en_US/champion/" + name_to_id.get(name) + \
                     ".json"
            r = requests.get(jsonURL)
            with open(path, "wb") as outfile:
                outfile.write(r.content)


def get_champ_pics(name_to_id):
    for name in name_to_id:
        path = "./champs/" + name + ".png"
        if not os.path.isfile(path):
            imgURL = "http://ddragon.leagueoflegends.com/cdn/10.25.1/img/champion/" + name_to_id.get(name) + ".png"
            r = requests.get(imgURL)
            with open(path, "wb") as outfile:
                outfile.write(r.content)


def get_spell_pics():
    spells = ["Heal", "Haste", "Barrier", "Exhaust", "Flash", "Teleport", "Smite", "Boost", "Dot"]
    for s in spells:
        path = "./spells/" + s + ".png"
        if not os.path.isfile(path):
            imgURL = "http://ddragon.leagueoflegends.com/cdn/10.25.1/img/spell/Summoner" + s + ".png"
            r = requests.get(imgURL)
            with open(path, "wb") as outfile:
                outfile.write(r.content)


def get_skill_pics(name_to_id):
    d = "./champ_json/"
    for f in os.listdir(d):
        c = json.load(open(d + f, encoding="utf8"))
        for s in c["data"][name_to_id[f[:len(f) - 5]]]["spells"][:3]:
            path = "./skills/" + s["id"] + ".png"
            if not os.path.isfile(path):
                imgURL = "http://ddragon.leagueoflegends.com/cdn/10.25.1/img/spell/" + s["id"] + ".png"
                r = requests.get(imgURL)
                with open(path, "wb") as outfile:
                    outfile.write(r.content)


def get_item_pics(id_to_name):
    item_id = list(id_to_name.keys())
    for i in item_id:
        path = "./items/" + id_to_name[i] + ".png"
        if not os.path.isfile(path):
            itemURL = "http://ddragon.leagueoflegends.com/cdn/10.25.1/img/item/" + i + ".png"
            r = requests.get(itemURL)
            with open(path, "wb") as outfile:
                outfile.write(r.content)


def get_champ(champ, role=""):
    champ_file = remove_html_tags(urllib.request.urlopen("https://na.op.gg/champion/" + champ +
                                                         "/statistics" + role + "".lower()).read().decode("utf-8"))
    champ_file = re.split(r"Win Ratio\s*[0-9]{2}.[0-9]{2}%\s*Counter", champ_file[champ_file.find("Strong against") +
                                                                                  14:].strip())
    champ_list = []
    for c in champ_file[:len(champ_file) - 1]:
        if " ".join(c.split()) == "Nunu &amp; Willump":
            champ_list.append(" ".join(c.replace("&amp;", "&").split()))
        else:
            champ_list.append(" ".join(c.split()))
    return champ_list


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def display_champ(champ, role=""):
    champ_dict, layout, i, n, item_dict, rune_dict = get_champ_dict(''), [], 0, 2, get_item_dict(), get_rune_dict()
    champ_list = get_champ(champ_dict[champ], role)
    layout = create_roles(layout)
    layout = search_bar(layout)
    layout.append([])
    layout[1].append(sg.Text("Weak Against:", justification="center"))
    for row in range(2):
        layout.append([])
        layout.append([])
        if row == 1:
            layout.append([])
            layout[4].append(sg.Text("Strong Against:", justification="center"))
            n += 1
        for col in range(3):
            layout[2 * row + n].append(sg.Button(image_filename="./champs/" + champ_list[i] + ".png", image_size=(60,
                                                                                                                  60),
                                                 image_subsample=2))
            layout[2 * row + n + 1].append(sg.Text(champ_list[i], size=(8, 1), justification="center", pad=(2, 0)))
            i += 1
    layout = display_spells(layout, champ_dict, champ)
    layout = display_skills(layout, champ_dict, champ)
    layout = display_item(layout, champ_dict, item_dict, champ)
    layout = display_runes(layout, champ_dict, rune_dict, champ)
    pos = re.search(r"champion-stats-header__position__role\">(Top|Jungle|Middle|Bottom|Support)</span>",
                    urllib.request.urlopen("https://na.op.gg/champion/" + champ_dict[champ] + "/statistics").read().
                    decode("utf8")).group(1)
    return sg.Window(champ + " " + pos, layout)


def display_spells(layout, champ_dict, champ):
    layout[2].append(sg.Text(size=(10, 0)))
    layout[3].append(sg.Text(size=(10, 0)))
    f = urllib.request.urlopen("https://na.op.gg/champion/" + champ_dict[champ] + "/statistics/").read().decode("utf-8")
    f = re.split("champion-stats__list__item\">\\s*<img src=\"", f)
    for spell in range(2):
        m = re.search(r"(//opgg-static\.akamaized\.net/images/lol/spell/Summoner(Heal|Haste|Barrier|Exhaust|Flash|"
                      r"Teleport|Smite|Boost|Dot)\.png\?image=c_scale,q_auto,w_42&amp;v=\d{10})", f[spell + 1])
        if m:
            layout[2].append(sg.Button(image_filename="./spells/" + m.group(2) + ".png", image_size=(60, 60)))
            layout[3].append(sg.Text(m.group(2), size=(8, 1), justification="center", pad=(2, 0)))
    return layout


def display_skills(layout, champ_dict, champ):
    layout[5].append(sg.Text(size=(10, 0)))
    layout[6].append(sg.Text(size=(10, 0)))
    f = urllib.request.urlopen("https://na.op.gg/champion/" + champ_dict[champ] + "/statistics/").read().decode("utf-8")
    c = json.load(open("./champ_json/" + champ + ".json", encoding="utf8"))["data"][champ_dict[champ]]["spells"]
    for spell in range(3):
        m = re.search("(<span>([QWE])</span>)", f)
        f = f.replace(m.group(1), "")
        if m.group(2) == "Q":
            layout[5].append(sg.Button(image_filename="./skills/" + c[0]["id"] + ".png", image_size=(60, 60)))
        elif m.group(2) == "W":
            layout[5].append(sg.Button(image_filename="./skills/" + c[1]["id"] + ".png", image_size=(60, 60)))
        elif m.group(2) == "E":
            layout[5].append(sg.Button(image_filename="./skills/" + c[2]["id"] + ".png", image_size=(60, 60)))
        layout[6].append(sg.Text(m.group(2), size=(8, 1), justification="center", pad=(2, 0)))
    return layout


def display_item(layout, champ_dict, item_dict, champ):
    layout.append([])
    layout[7].append(sg.Text("Items", justification="center"))
    layout.append([])
    layout.append([])
    f = urllib.request.urlopen("https://na.op.gg/champion/" + champ_dict[champ] + "/statistics/").read().decode("utf-8")
    item_list = find_items(f, "Starter Items", 1)
    item_list.extend(find_items(f, "Recommended Builds", 5))
    item_list.extend(find_items(f, "Boots</th>", 1))
    for i in item_list:
        layout[8].append(sg.Button(image_filename="./items/" + item_dict[i] + ".png", image_size=(60, 60)))
        layout[9].append(sg.Text(item_dict[i], size=(8, 1), justification="center", pad=(2, 0)))
    return layout


def find_items(f, keyword, amount):
    item_list = []
    s = re.split(keyword, f)[1]
    while len(item_list) != amount:
        m = re.search(r"(//opgg-static\.akamaized\.net/images/lol/item/(\d{4})\.png\?image=q_auto:best&amp;"
                      r"v=\d{10})", s)
        s = s.replace(m.group(1), "")
        item_list.append(m.group(2))
    return item_list


def display_runes(layout, champ_dict, rune_dict, champ):
    layout.append([])
    layout[10].append(sg.Text("Runes", justification="center"))
    layout.append([])
    layout.append([])
    f = urllib.request.urlopen("https://na.op.gg/champion/" + champ_dict[champ] + "/statistics/").read().decode("utf-8")
    f = re.split("tabItem ChampionKeystoneRune-1", f)[1]
    for i in range(11):
        m = re.search(r"(//opgg-static\.akamaized\.net/images/lol/perk(Style)*(Shard)*/(\d{4})\.png\?image=q_auto:best&"
                      r"amp;v=\d{10})", f)
        f = f.replace(m.group(1), "", 1)
        layout[11].append(sg.Button(image_filename="./runes/" + rune_dict[int(m.group(4))].replace(" ", "").
                                    replace(":", "") + ".png", image_size=(60, 60)))
        layout[12].append(sg.Text(rune_dict[int(m.group(4))], size=(8, 1), justification="center", pad=(2, 0)))
    return layout


def search_bar(layout):
    layout.append([])
    for col in range(5):
        layout[0].append(sg.Text('', size=(7, 0)))
    layout[0].append(sg.Input(justification='right', size=(52, 0), key='input'))
    layout[0].append(sg.Button('Search', key='search', bind_return_key=True))
    return layout


def create_roles(layout):
    if len(layout) == 0:
        layout.append([])
    roles = ["Top", "Jungle", "Mid", "Bottom", "Support"]
    for r in roles:
        layout[0].append(sg.Button(r, size=(7, 0), key=r.lower()))
    return layout


def update_layout(search_input):
    champ_dict, layout, i = get_champ_dict(search_input), [], 0
    layout = search_bar(layout)
    for row in range(10):
        layout.append([])
        layout.append([])
        for col in range(16):
            if i != (len(list(champ_dict.keys()))):
                if i != len(list(champ_dict.keys())) and search_input.strip() in list(champ_dict.keys())[i].lower():
                    layout[2 * row + 1].append(sg.Button(image_filename="./champs/" + list(champ_dict.keys())[i] +
                                                                        ".png", image_size=(60, 60), image_subsample=2,
                                                         key=list(champ_dict.keys())[i]))
                    layout[2 * row + 2].append(sg.Text(list(champ_dict.keys())[i], size=(8, 1), justification='center',
                                                       pad=(2, 0)))
                i += 1
    return layout


def create_window(search_input):
    layout = update_layout(search_input)
    return sg.Window('champs', layout)


if __name__ == "__main__":
    champ_dict_general = get_champ_dict('')
    window = create_window('')
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == 'search':
            if values['input'].strip() != '':
                window.close()
                window = create_window(values['input'].strip())
            else:
                window.close()
                window = create_window('')
        else:
            window.close()
            window = display_champ(event)
    window.close()


