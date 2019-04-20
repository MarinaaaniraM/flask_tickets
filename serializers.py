def tickets_serializer(data):
    tickets = {}
    comments = {}

    for item in data:
        ticket_id = item.get('c.ticket_id')
        if ticket_id is not None:
            current_array = comments.get(ticket_id, [])
            current_array.append({
                'id': item.get('c.id'),
                'text': item.get('c.text'),
                'email': item.get('c.email'),
                'created_at': item.get('c.created_at').strftime("%d.%m.%Y, %H:%M:%S"),
                'updated_at': item.get('c.updated_at').strftime("%d.%m.%Y, %H:%M:%S"),
            })

            comments.update({
                ticket_id: current_array
            })

        ticket_id = item.get('t.id')
        tickets.update({
            ticket_id: {
                'id': ticket_id,
                'theme': item.get('t.theme'),
                'text': item.get('t.text'),
                'email': item.get('t.email'),
                'state': item.get('t.state'),
                'created_at': item.get('t.created_at').strftime("%d.%m.%Y, %H:%M:%S"),
                'updated_at': item.get('t.updated_at').strftime("%d.%m.%Y, %H:%M:%S"),
                'comments': comments.get(ticket_id, {})
            }
        })
    return tickets
