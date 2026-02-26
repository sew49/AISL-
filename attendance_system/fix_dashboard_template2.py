# Read the dashboard template
with open('templates/admin/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the header section
old_header = '''                <thead>
                    <tr class="bg-blue-50 text-blue-900">
                        <th class="p-3 border">ID</th>
                        <th class="p-3 border">Staff Name</th>
                        <th class="p-3 border">2021</th>
                        <th class="p-3 border">2022</th>
                        <th class="p-3 border">2023</th>
                        <th class="p-3 border">2024</th>
                        <th class="p-3 border">2025</th>
                        <th class="p-3 border">2026</th>
                    </tr>
                </thead>'''

new_header = '''                <thead>
                    <tr class="bg-blue-50 text-blue-900">
                        <th class="p-2 border" rowspan="2">ID</th>
                        <th class="p-2 border" rowspan="2">Staff Name</th>
                        <th class="p-2 border text-center bg-blue-100" colspan="2">2021</th>
                        <th class="p-2 border text-center bg-blue-100" colspan="2">2022</th>
                        <th class="p-2 border text-center bg-blue-100" colspan="2">2023</th>
                        <th class="p-2 border text-center bg-blue-100" colspan="2">2024</th>
                        <th class="p-2 border text-center bg-blue-100" colspan="2">2025</th>
                        <th class="p-2 border text-center bg-blue-100" colspan="2">2026</th>
                    </tr>
                    <tr class="bg-blue-50 text-blue-900">
                        <th class="p-2 border text-center text-xs">Annual</th>
                        <th class="p-2 border text-center text-xs bg-red-50">Sick</th>
                        <th class="p-2 border text-center text-xs">Annual</th>
                        <th class="p-2 border text-center text-xs bg-red-50">Sick</th>
                        <th class="p-2 border text-center text-xs">Annual</th>
                        <th class="p-2 border text-center text-xs bg-red-50">Sick</th>
                        <th class="p-2 border text-center text-xs">Annual</th>
                        <th class="p-2 border text-center text-xs bg-red-50">Sick</th>
                        <th class="p-2 border text-center text-xs">Annual</th>
                        <th class="p-2 border text-center text-xs bg-red-50">Sick</th>
                        <th class="p-2 border text-center text-xs">Annual</th>
                        <th class="p-2 border text-center text-xs bg-red-50">Sick</th>
                    </tr>
                </thead>'''

content = content.replace(old_header, new_header)

# Replace the 2021 data cells
old_2021 = '''                        <td class="p-3 border text-center">
                            {% if row.years[2021] %}
                                {% if row.years[2021] == row.years[2021]|int %}
                                    {{ row.years[2021]|int }}
                                {% else %}
                                    {{ row.years[2021] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

new_2021 = '''                        <td class="p-2 border text-center bg-blue-50">
                            {% if row.annual[2021] %}
                                {% if row.annual[2021] == row.annual[2021]|int %}
                                    {{ row.annual[2021]|int }}
                                {% else %}
                                    {{ row.annual[2021] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-2 border text-center bg-red-50">
                            {% if row.sick[2021] %}
                                {% if row.sick[2021] == row.sick[2021]|int %}
                                    {{ row.sick[2021]|int }}
                                {% else %}
                                    {{ row.sick[2021] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

content = content.replace(old_2021, new_2021)

# Replace the 2022 data cells
old_2022 = '''                        <td class="p-3 border text-center">
                            {% if row.years[2022] %}
                                {% if row.years[2022] == row.years[2022]|int %}
                                    {{ row.years[2022]|int }}
                                {% else %}
                                    {{ row.years[2022] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

new_2022 = '''                        <td class="p-2 border text-center bg-blue-50">
                            {% if row.annual[2022] %}
                                {% if row.annual[2022] == row.annual[2022]|int %}
                                    {{ row.annual[2022]|int }}
                                {% else %}
                                    {{ row.annual[2022] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-2 border text-center bg-red-50">
                            {% if row.sick[2022] %}
                                {% if row.sick[2022] == row.sick[2022]|int %}
                                    {{ row.sick[2022]|int }}
                                {% else %}
                                    {{ row.sick[2022] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

content = content.replace(old_2022, new_2022)

# Replace the 2023 data cells
old_2023 = '''                        <td class="p-3 border text-center">
                            {% if row.years[2023] %}
                                {% if row.years[2023] == row.years[2023]|int %}
                                    {{ row.years[2023]|int }}
                                {% else %}
                                    {{ row.years[2023] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

new_2023 = '''                        <td class="p-2 border text-center bg-blue-50">
                            {% if row.annual[2023] %}
                                {% if row.annual[2023] == row.annual[2023]|int %}
                                    {{ row.annual[2023]|int }}
                                {% else %}
                                    {{ row.annual[2023] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-2 border text-center bg-red-50">
                            {% if row.sick[2023] %}
                                {% if row.sick[2023] == row.sick[2023]|int %}
                                    {{ row.sick[2023]|int }}
                                {% else %}
                                    {{ row.sick[2023] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

content = content.replace(old_2023, new_2023)

# Replace the 2024 data cells
old_2024 = '''                        <td class="p-3 border text-center">
                            {% if row.years[2024] %}
                                {% if row.years[2024] == row.years[2024]|int %}
                                    {{ row.years[2024]|int }}
                                {% else %}
                                    {{ row.years[2024] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

new_2024 = '''                        <td class="p-2 border text-center bg-blue-50">
                            {% if row.annual[2024] %}
                                {% if row.annual[2024] == row.annual[2024]|int %}
                                    {{ row.annual[2024]|int }}
                                {% else %}
                                    {{ row.annual[2024] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-2 border text-center bg-red-50">
                            {% if row.sick[2024] %}
                                {% if row.sick[2024] == row.sick[2024]|int %}
                                    {{ row.sick[2024]|int }}
                                {% else %}
                                    {{ row.sick[2024] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

content = content.replace(old_2024, new_2024)

# Replace the 2025 data cells
old_2025 = '''                        <td class="p-3 border text-center">
                            {% if row.years[2025] %}
                                {% if row.years[2025] == row.years[2025]|int %}
                                    {{ row.years[2025]|int }}
                                {% else %}
                                    {{ row.years[2025] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

new_2025 = '''                        <td class="p-2 border text-center bg-blue-50">
                            {% if row.annual[2025] %}
                                {% if row.annual[2025] == row.annual[2025]|int %}
                                    {{ row.annual[2025]|int }}
                                {% else %}
                                    {{ row.annual[2025] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-2 border text-center bg-red-50">
                            {% if row.sick[2025] %}
                                {% if row.sick[2025] == row.sick[2025]|int %}
                                    {{ row.sick[2025]|int }}
                                {% else %}
                                    {{ row.sick[2025] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

content = content.replace(old_2025, new_2025)

# Replace the 2026 data cells
old_2026 = '''                        <td class="p-3 border text-center">
                            {% if row.years[2026] %}
                                {% if row.years[2026] == row.years[2026]|int %}
                                    {{ row.years[2026]|int }}
                                {% else %}
                                    {{ row.years[2026] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

new_2026 = '''                        <td class="p-2 border text-center bg-blue-50">
                            {% if row.annual[2026] %}
                                {% if row.annual[2026] == row.annual[2026]|int %}
                                    {{ row.annual[2026]|int }}
                                {% else %}
                                    {{ row.annual[2026] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-2 border text-center bg-red-50">
                            {% if row.sick[2026] %}
                                {% if row.sick[2026] == row.sick[2026]|int %}
                                    {{ row.sick[2026]|int }}
                                {% else %}
                                    {{ row.sick[2026] }}
                                {% endif %}
                            {% else %}
                                -
                            {% endif %}
                        </td>'''

content = content.replace(old_2026, new_2026)

# Write back
with open('templates/admin/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Dashboard template updated!')
