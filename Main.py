import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from analizador_sintactico import *

# Función para actualizar la numeración de líneas
def actualizar_numeros(event=None):
    lineas.config(state='normal')
    lineas.delete('1.0', END)
    inicio, _ = code.index("@0,0").split('.')
    fin, _ = code.index(f"@0,{code.winfo_height()}").split('.')
    numeros = '\n'.join(str(i) for i in range(int(inicio), int(fin) + 1))
    lineas.insert('1.0', numeros)
    lineas.config(state='disabled')

# Sincronización de scroll entre líneas y el editor
def sincronizar_scroll(*args):
    lineas.yview(*args)
    code.yview(*args)

# Función para crear una nueva pestaña con un nuevo archivo
def nuevo_archivo():
    nueva_pestaña = Frame(notebook, bg=bg_color)
    notebook.add(nueva_pestaña, text="Nuevo Archivo")
    configurar_editor(nueva_pestaña)
    añadir_cerrar_pestaña(nueva_pestaña)

# Función para cerrar una pestaña
def cerrar_pestaña(pestaña):
    index = notebook.index(pestaña)
    editor_actual = pestaña.winfo_children()[0].winfo_children()[1]
    contenido = editor_actual.get('1.0', END).strip()
    if contenido:
        respuesta = messagebox.askyesnocancel("Guardar", "¿Deseas guardar los cambios antes de cerrar?")
        if respuesta is None:
            return  # Cancela el cierre si el usuario selecciona "Cancelar"
        elif respuesta:  # Si selecciona "Sí"
            guardar_archivo(editor_actual)
    notebook.forget(index)  # Cierra la pestaña


# Función para guardar el archivo
def guardar_archivo(editor):
    archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(editor.get('1.0', END).strip())
        messagebox.showinfo("Guardar", "Archivo guardado exitosamente.")

# Añadir botón de cerrar a una pestaña
def añadir_cerrar_pestaña(pestaña):
    index = notebook.index(pestaña)
    titulo = notebook.tab(index, option="text")
    notebook.tab(index, text=f"{titulo}  ✕")
    notebook.bind('<Button-1>', manejar_cerrar_pestaña)

# Manejar clic en la cruz para cerrar pestañas
# Manejar clic en la cruz para cerrar pestañas
def manejar_cerrar_pestaña(event=None):
    pestaña_id = notebook.select()  # Obtén el identificador de la pestaña seleccionada
    print(f"Intentando cerrar: {pestaña_id}")
    try:
        pestaña_widget = notebook.nametowidget(pestaña_id)  # Convierte el identificador al widget correspondiente
        cerrar_pestaña(pestaña_widget)
    except Exception as e:
        print(f"Error al intentar cerrar la pestaña: {e}")





# Función para configurar un editor en una pestaña
def configurar_editor(tab):
    frameText = Frame(tab, bg=bg_color)
    frameText.pack(fill=BOTH, expand=True)
    global lineas, code
    lineas = Text(frameText, bg='#252526', fg=fg_color, width=4, padx=5, pady=5, state='disabled')
    lineas.pack(side=LEFT, fill=Y)
    code = Text(frameText, bg='#FFFFFF', fg='#000000', insertbackground=fg_color, undo=True, wrap='none')
    code.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10), pady=(0, 10))
    scroll_y = Scrollbar(frameText, orient=VERTICAL, command=sincronizar_scroll)
    scroll_y.pack(side=RIGHT, fill=Y)
    lineas.config(yscrollcommand=scroll_y.set)
    code.config(yscrollcommand=scroll_y.set)
    code.bind('<KeyRelease>', actualizar_numeros)
    code.bind('<MouseWheel>', actualizar_numeros)
    code.bind('<Return>', actualizar_numeros)
    code.bind('<BackSpace>', actualizar_numeros)
    actualizar_numeros()

# Función para seleccionar un directorio
def seleccionar_directorio():
    global directorio_actual
    directorio_actual = filedialog.askdirectory()
    if directorio_actual:
        mostrar_contenido_directorio(directorio_actual)
    else:
        lista_directorio.delete(0, END)
        lista_directorio.insert(END, "Directorio no seleccionado")

# Actualiza el nombre del directorio en el navegador
def actualizar_label_directorio():
    labelDirectorio.config(text=f"Navegador de directorios: {directorio_actual}")

# Función para mostrar el contenido del directorio en la lista
def mostrar_contenido_directorio(path):
    lista_directorio.delete(0, END)
    try:
        archivos = os.listdir(path)
        lista_directorio.insert(END, ".. (Subir)")
        for archivo in archivos:
            lista_directorio.insert(END, archivo)
        actualizar_label_directorio()
    except Exception as e:
        lista_directorio.insert(END, f"Error: {e}")

# Función para abrir un archivo en una nueva pestaña
def abrir_archivo(path):
    try:
        with open(path, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
        nueva_pestaña = Frame(notebook, bg=bg_color)
        notebook.add(nueva_pestaña, text=os.path.basename(path))
        configurar_editor(nueva_pestaña)
        code.insert('1.0', contenido)
        actualizar_numeros()
        añadir_cerrar_pestaña(nueva_pestaña)
    except Exception as e:
        consola.config(state='normal')
        consola.insert(END, f"Error al abrir archivo: {e}\n")
        consola.config(state='disabled')

# Función para manejar clics en la lista de directorios
def manejar_click_directorio(event):
    global directorio_actual
    seleccion = lista_directorio.get(ACTIVE)
    if seleccion == ".. (Subir)":
        directorio_actual = os.path.dirname(directorio_actual)
    else:
        ruta_seleccionada = os.path.join(directorio_actual, seleccion)
        if os.path.isdir(ruta_seleccionada):
            directorio_actual = ruta_seleccionada
        elif os.path.isfile(ruta_seleccionada):
            abrir_archivo(ruta_seleccionada)
            return
    mostrar_contenido_directorio(directorio_actual)

def compilar():
    global contenido  # Definir 'contenido' como global para usarlo dentro de parse_program
    consola.config(state='normal')
    consola.delete('1.0', END)
    consola.config(state='disabled')

    for i in range(notebook.index('end')):
        pestaña = notebook.nametowidget(notebook.tabs()[i])  # Acceder a cada pestaña
        editor = pestaña.winfo_children()[0].winfo_children()[1]
        contenido = editor.get('1.0', END).strip()  # Almacenar el contenido de la pestaña en la variable 'contenido'

        if contenido:
            consola.config(state='normal')
            consola.insert(END, f"Compilando contenido de la pestaña {i + 1}\n")
            try:
                # Análisis léxico
                tokens = tokenize(contenido)
                consola.insert(END, "Análisis léxico exitoso.\n")
                consola.insert(END, "Tokens encontrados:\n")
                for idx, token in enumerate(tokens):
                    consola.insert(END, f"  {idx:2d} - {token[0]:<15} {token[1]}\n")

                # Análisis sintáctico
                consola.insert(END, "Iniciando análisis sintáctico...\n")
                try:
                    # Aquí ya puedes llamar a parse_program sin pasarle argumentos
                    parse_program()  # Usará el contenido que es global
                    consola.insert(END, "Análisis sintáctico exitoso.\n")
                    consola.insert(END, "Árbol de análisis generado correctamente.\n")
                except SyntaxError as se:
                    consola.insert(END, f"Error sintáctico: {se}\n")
                except Exception as e:
                    consola.insert(END, f"Error durante el análisis sintáctico: {e}\n")

            except Exception as e:
                consola.insert(END, f"Error durante la compilación: {e}\n")
            finally:
                consola.config(state='disabled')


# Interfaz principal
root = Tk()
root.title("COMPILADOR MUSICAL - V1.0")
root.configure(bg='#1e1e1e')
root.state('zoomed')

# Configuración de colores
fg_color = '#d4d4d4'
bg_color = '#1e1e1e'
button_bg_color = '#007acc'
button_fg_color = '#ffffff'

# Variables
directorio_actual = None

# Frame para los botones
frameButtons = Frame(root, bg=bg_color)
frameButtons.pack(side=TOP, fill=X)

btnNuevoArchivo = Button(frameButtons, text='Nuevo archivo', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'), command=nuevo_archivo)
btnNuevoArchivo.pack(side=LEFT, padx=10, pady=10)

btnSeleccionarDirectorio = Button(frameButtons, text='Seleccionar directorio', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'), command=seleccionar_directorio)
btnSeleccionarDirectorio.pack(side=LEFT, padx=10, pady=10)

btnGuardarArchivo = Button(frameButtons, text='Guardar archivo', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'))
btnGuardarArchivo.pack(side=LEFT, padx=10, pady=10)

btnCompilar = Button(frameButtons, text='Compilar', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'), command=compilar)
btnCompilar.pack(side=LEFT, padx=10, pady=10)

frameMain = PanedWindow(root, bg=bg_color, sashwidth=5)
frameMain.pack(fill=BOTH, expand=True)

frameDirectorio = Frame(frameMain, bg=bg_color)
frameMain.add(frameDirectorio, width=250)

labelDirectorio = Label(frameDirectorio, text="Navegador de directorios", bg=bg_color, fg=fg_color, font=('Arial', 10, 'bold'))
labelDirectorio.pack(fill=X)

lista_directorio = Listbox(frameDirectorio, bg='#252526', fg=fg_color, selectbackground=button_bg_color, selectforeground=button_fg_color)
lista_directorio.pack(fill=BOTH, expand=True, padx=5, pady=5)

lista_directorio.insert(END, "Directorio no seleccionado")
lista_directorio.bind('<Double-Button-1>', manejar_click_directorio)

notebook = ttk.Notebook(frameMain)
frameMain.add(notebook)

pestaña_inicial = Frame(notebook, bg=bg_color)
notebook.add(pestaña_inicial, text="Archivo 1")
configurar_editor(pestaña_inicial)
añadir_cerrar_pestaña(pestaña_inicial)

frameConsole = Frame(root, bg=bg_color)
frameConsole.pack(side=BOTTOM, fill=X)

consola = Text(frameConsole, bg='#252526', fg=fg_color, height=10, wrap='word', state='disabled')
consola.pack(fill=X, padx=10, pady=10)

root.mainloop()
