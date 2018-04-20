import sqlite3
import json
import plotly.plotly as py
import plotly.graph_objs as go
import getpets
import cats
import json

DBNAME = 'cats.db'

def process_command(command):
    command = command.split()
    if 'pie' in command:
        return pie(command)
    elif 'scatter' in command:
        return scatter(command)
    elif 'table'in command:
        return table(command)
    elif 'bar' in command:
        return bar(command)
    else:
        return "error"

# ex command: pie color size=XX #percent of cats of a certain size in each color
# ex command: pie pets location=MI//size=X//color=X #percent of pets in different breeds or sizes,  OR pets in michigan OR in a certain color (size/location optional)
def pie(command):
    results = []
    if command[1] == 'pets':
        select = '''SELECT B.Name, Count(*) '''
        from_join = ''' FROM 'Pets' AS P
        JOIN 'Breeds' AS B ON B.Id = P.BreedId '''
        group = ''' GROUP BY B.Id '''
        for word in command:
            if 'location=' in word:
                ind = command.index(word)
                where = ''' WHERE P.Location LIKE "%''' + command[ind].split("=")[1] + '''" '''
                title = "Percent of cats in each breed in " + command[ind].split("=")[1]
            if 'size=' in word:
                ind = command.index(word)
                where = ''' WHERE P.Size = "''' + command[ind].split("=")[1] + '''" '''
                title = '''Percent of {} cats in each breed '''.format(command[ind].split("=")[1])
            if 'color=' in word:
                ind = command.index(word)
                from_join += ''' JOIN 'BreedColors' AS BC ON BC.BreedId = B.Id
                JOIN Colors AS C on C.Id = BC.ColorId'''
                where = ''' WHERE C.Name Like "%''' + command[ind].split("=")[1] + '''%" '''
                title = '''Percentage of {} cats in each breed'''.format(command[ind].split("=")[1])
        statement = select + from_join + where + group
    elif command[1] == 'color':
        select = '''SELECT C.Name, Count(*) FROM BreedColors as BC '''
        join = ''' JOIN 'Colors' AS C ON BC.ColorId = C.Id
            JOIN 'Breeds' AS B on BC.BreedId = B.Id '''
        group = ''' GROUP BY C.Name '''
        where = ''
        for word in command:
            if 'size=' in word:
                ind = command.index(word)
                where = '''WHERE B.Size = "''' + command[ind].split("=")[1] + '''" '''
        statement = select + join + where + group
        title = "Percent of Breeds that come in each color"
    else:
        return 'error'
        # print(statement)
    with sqlite3.connect(DBNAME) as conn:
        cur = conn.cursor()
        cur.execute(statement)
        labels = []
        values = []
        for row in cur:
            results.append(row)
            labels.append(row[0])
            values.append(row[1])
    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value',
                   textfont=dict(size=20),
                   marker=dict(line=dict(color='#000000', width=2)))
    fig = {'data':[trace], 'layout':{'title':title}}
    py.plot(fig, filename='cat_pie_chart')
    return(results)

# ex command: scatter x=trait y=othertrait color=XX OR size=XX
def scatter(command):
    results = []
    select = '''SELECT B.Name,  '''
    from_join = ''' FROM BreedColors AS BC
    JOIN 'Colors' AS C ON BC.ColorId = C.Id
        JOIN 'Breeds' AS B on BC.BreedId = B.Id '''
    xtrait = ''
    ytrait = ''
    where = ''
    for word in command:
        if 'color=' in word:
            ind = command.index(word)
            where = ''' WHERE C.Name LIKE "''' + command[ind].split("=")[1] +'" '
        elif 'size=' in word:
            ind = command.index(word)
            where = ''' WHERE B.Size = "''' + command[ind].split("=")[1] + '" '
        if 'x=' in word:
            ind = command.index(word)
            xtrait = command[ind].split("=")[1]
            select += '''B.''' + xtrait
        elif 'y=' in word:
            ind = command.index(word)
            ytrait = command[ind].split("=")[1]
            select += ''', B.''' + ytrait
    if xtrait == '':
        xtrait = 'AffectionLevel'
        select += '''B.''' + xtrait
    if ytrait == '':
        ytrait = 'Intelligence'
        select += ''', B.''' + ytrait
    group = ''' GROUP BY B.Name '''
    statement = select + from_join + where + group
    data_list = []
    with sqlite3.connect(DBNAME) as conn:
        cur = conn.cursor()
        cur.execute(statement)
        for row in cur:
            results.append(row)
            breed = row[0]
            x = row[1]
            y = row[2]
            trace0= go.Scatter(
            x= row[1],
            y= row[2],
            mode= 'markers',
            marker = dict(
                size = 10,
                color = 'rgba(152, 0, 0, .8)',
                line = dict(width = 2, color = 'rgb(0, 0, 0)')),
            text= breed)
            data_list.append(trace0)
    layout= go.Layout(
    title= 'Breeds by {} and {}'.format(xtrait, ytrait),
    hovermode= 'closest',
    xaxis= dict(
        title= xtrait,
    ),
    yaxis=dict(
        title= ytrait,
    ))
    fig= go.Figure(data=data_list, layout=layout)
    py.plot(fig)
    return results

# ex command: table /breed=XX OR color=XX OR size=XX / trait=XX (default = AffectionLevel) /
def table(command):
    results = []
    select = '''SELECT B.Name, B.Size, B.Popularity, B.LifeSpan'''
    from_join = ''' FROM BreedColors AS BC
    JOIN 'Colors' AS C ON BC.ColorId = C.Id
        JOIN 'Breeds' AS B on BC.BreedId = B.Id '''
    order = ''
    where = ''
    for word in command:
        if 'top' in word:
            ind = command.index(word)
            lim = " DESC "
            lim += " LIMIT " + command[ind].split("=")[1] + " "
        elif 'bottom' in word:
            ind = command.index(word)
            # print(command[ind].split("=")[1])
            lim = " LIMIT " + command[ind].split("=")[1] + " "## deals with top and bottom
        else:
            lim = " DESC LIMIT 10 "
        if 'breed' in word:
            ind = command.index(word)
            breedname = command[ind].split("=")[1]
            if "_" in breedname:
                breedname = breedname.replace("_", " ")
            where = ''' WHERE B.Name = "''' + breedname +'" '
        elif 'color' in word:
            ind = command.index(word)
            where = ''' WHERE C.Name LIKE "''' + command[ind].split("=")[1] + '" '
        elif 'size' in word:
            ind = command.index(word)
            where = ''' WHERE B.Size = "''' + command[ind].split("=")[1] + '" '
        if 'trait' in word:
            ind = command.index(word)
            trait = command[ind].split("=")[1]
            order = ''' ORDER BY B.''' + command[ind].split("=")[1] + " "
            select += ''', B.''' + command[ind].split("=")[1] + " "
    if order == '':
        trait = 'AffectionLevel'
        order = ''' ORDER BY B.AffectionLevel '''
        select += ''', B.AffectionLevel '''
    group = ''' GROUP BY B.Name '''
    statement = select + from_join + where + group + order + lim

    c1 = []
    c2 = []
    c3 = []
    c4 = []
    c5 = []
    with sqlite3.connect(DBNAME) as conn:
        cur = conn.cursor()
        cur.execute(statement)
        for row in cur:
            results.append(row)
            c1.append(row[0])
            c2.append(row[1])
            c3.append(row[2])
            c4.append(row[3])
            c5.append(row[4])
    trace = go.Table(
    header=dict(values=['Name', 'Size','Popularity', 'LifeSpan', trait], line = dict(color='#7D7F80'),
                fill = dict(color='#a1c3d1'),
                align = ['left'] * 5),
    cells=dict(values=[c1, c2, c3, c4, c5], line = dict(color='#7D7F80'),
               fill = dict(color='#EDFAFF'),
               align = ['left'] * 5))
    layout = dict(width=400, height=300, title="Breed Data")
    data = [trace]
    fig=dict(data=data, layout=layout)
    py.plot(data, filename = 'breed_table')
    return results

# ex comand: bar breed=XX (shows behavior stats for breed)
#ex command: bar compare breed1=xx breed2=xx
def bar(command):
    results = []
    if command[1] == 'compare':
        select = '''SELECT * FROM Breeds '''
        breed1 = ''
        breed2 = ''
        for word in command:
            if 'breed1=' in word:
                ind = command.index(word)
                breed1 = command[ind].split("=")[1]
                if "_" in breed1:
                    breed1=breed1.replace("_", " ")
                where1 = '''WHERE Name LIKE "''' + breed1 + '" '
            if 'breed2=' in word:
                ind = command.index(word)
                breed2 = command[ind].split("=")[1]
                if "_" in breed1:
                    breed2=breed2.replace("_", " ")
                where2 = '''WHERE Name LIKE "''' + breed2 + '" '

        if breed1 == '' or breed2 =='':
            return 'error'

        with sqlite3.connect(DBNAME) as conn:
            cur = conn.cursor()
            statement = select + where1
            cur.execute(statement)
            for row in cur:
                results.append(row)
                x = ['Popularity', 'Affection Level', 'Energy Level', 'Number of Health Issues', 'Intelligence', 'Amount of Shedding']
                y = [row[2], row[5], row[6], row[7], row[8], row[9]]
                trace1 = go.Bar(
                    x=x,
                    y=y,
                    name='trait rankings for {}'.format(breed1))
            statement = select + where2
            cur.execute(statement)
            for row in cur:
                results.append(row)
                x = ['Popularity', 'Affection Level', 'Energy Level', 'Number of Health Issues', 'Intelligence', 'Amount of Shedding']
                y = [row[2], row[5], row[6], row[7], row[8], row[9]]
                trace2 = go.Bar(
                    x=x,
                    y=y,
                    name='trait rankings for {}'.format(breed2))

            data = [trace1, trace2]
            layout = go.Layout(barmode='group', title = 'comparison of traits between {} and {}'.format(breed1, breed2))

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='comparison_{}_{}'.format(breed1, breed2))
        return results
    elif 'breed' in command[1]:
        select = '''SELECT * FROM Breeds '''
        for word in command:
            ind = command.index(word)
            breed = command[1].split("=")[1]
            if "_" in breed:
                breed=breed.replace("_", " ")
        where = '''WHERE Name LIKE "''' + breed + '" '
        statement = select + where
        with sqlite3.connect(DBNAME) as conn:
            cur = conn.cursor()
            cur.execute(statement)
            for row in cur:
                results.append(row)
                x = ['Popularity', 'Affection Level', 'Energy Level', 'Health Issues', 'Intelligence', 'Amount of Shedding']
                y = [row[2], row[5], row[6], row[7], row[8], row[9]]
                data = [go.Bar(
                    x=x,
                    y=y,
                    name=breed)]
                layout = go.Layout(title='trait rankings for {}'.format(breed))
                fig = go.Figure(data=data, layout=layout)
                py.plot(fig, filename='{}_traits'.format(breed))
        return results
    else:
        return 'error'

def interactive_prompt():
    inp = ''
    while inp != "exit":
        inp = input("Type a command:  ")
        if inp == 'exit':
            break
        if inp.split()[0] not in ['bar', 'pie', 'table', 'scatter', 'help']:
            print("invalid command: '{}'. please try again.".format(inp))
            continue
        resp = process_command(inp)
        if resp == 'error':
            print("invalid command: '{}' please try again.".format(inp))


if __name__ == '__main__':
    interactive_prompt()
