def prepare_text(text: str):
    res_text = ""
    while True:
        left_part, trash, right_part = text.partition('<img')
        res_text += left_part
        if right_part == '':
            break
        left_part, trash, right_part = right_part.partition('>')
        res_text += right_part
        text = right_part
    return res_text


if __name__ == "__main__":
    print(prepare_text('''<a href="https://freelancehunt.com/profile/show/freelancehunt.html"> <img src="https://content.freelancehunt.com/profile/photo/50/freelancehunt.png" class="vertical avatar-container avatar-container-16" alt=""></a> <a href="/profile/show/freelancehunt.html">freelancehunt</a>
Читаем на выходных: — <a href="https://freelancehunt.com/blog/chitaiem-na-vykhodnykh-rabochieie-pokolieniie-molodieiet-ghrivnievyie-kupiury-zamieniaiutsia-a-rabotniki-nie-pri-dielakh/?utm_source=freelancehunt&amp;utm_medium=feed&amp;utm_campaign=blog-teaser" target="_blank">рабочее поколение молодеет, гривневые купюры будут заменены, а работники не при делах…</a> <img src="https://freelancehunt.com/static/images/fugu/new-text.png" width="16" height="16">'''))
