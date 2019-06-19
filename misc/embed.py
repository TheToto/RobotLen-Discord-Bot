from discord import embeds


def queue_embed(queue):
    res = embeds.Embed(title="Musiques en attente", type="rich")
    np_str = "Aucune musique en cours"
    if queue.is_playing():
        np_str = queue.current.get('title')
    res.add_field(name="Lecture en cours", value=np_str, inline=False)

    q_str = ''
    i = 1
    for item in queue.queue:
        q_str += str(i) + ". " + item.get('title') + "\n"
        i += 1
    if q_str == '':
        q_str = 'Aucune musique en attente.'
    res.add_field(name='À vénir', value=q_str, inline=False)

    return res
