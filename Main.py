import os
from tkinter import *
from tkinter import ttk, filedialog


# Función para actualizar la numeración de líneas
def actualizar_numeros(event=None):
    lineas.config(state='normal')
    lineas.delete('1.0', END)

    # Obtener el rango de líneas visibles
    inicio, _ = code.index("@0,0").split('.')
    fin, _ = code.index(f"@0,{code.winfo_height()}").split('.')

    # Generar números de línea correspondientes
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


# Función para configurar un editor en una pestaña
def configurar_editor(tab):
    frameText = Frame(tab, bg=bg_color)
    frameText.pack(fill=BOTH, expand=True)

    # Numeración de líneas
    global lineas, code
    lineas = Text(frameText, bg='#252526', fg=fg_color, width=4, padx=5, pady=5, state='disabled')
    lineas.pack(side=LEFT, fill=Y)

    # Editor de código
    code = Text(frameText, bg='#FFFFFF', fg='#000000', insertbackground=fg_color, undo=True, wrap='none')  # Color negro
    code.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10), pady=(0, 10))

    # Barra de desplazamiento vertical compartida
    scroll_y = Scrollbar(frameText, orient=VERTICAL, command=sincronizar_scroll)
    scroll_y.pack(side=RIGHT, fill=Y)

    # Vincular el scroll entre ambos widgets
    lineas.config(yscrollcommand=scroll_y.set)
    code.config(yscrollcommand=scroll_y.set)

    # Vincular eventos para actualizar la numeración de líneas
    code.bind('<KeyRelease>', actualizar_numeros)
    code.bind('<MouseWheel>', actualizar_numeros)
    code.bind('<Return>', actualizar_numeros)
    code.bind('<BackSpace>', actualizar_numeros)

    # Inicializar numeración
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
        lista_directorio.insert(END, ".. (Subir)")  # Para ir al directorio anterior
        for archivo in archivos:
            lista_directorio.insert(END, archivo)
        actualizar_label_directorio()  # Actualiza el label con el directorio actual
    except Exception as e:
        lista_directorio.insert(END, f"Error: {e}")


# Función para abrir un archivo en una nueva pestaña
def abrir_archivo(path):
    try:
        with open(path, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()

        # Crear nueva pestaña y configurar el editor
        nueva_pestaña = Frame(notebook, bg=bg_color)
        notebook.add(nueva_pestaña, text=os.path.basename(path))
        configurar_editor(nueva_pestaña)

        # Insertar contenido del archivo en el editor
        code.insert('1.0', contenido)
        actualizar_numeros()  # Actualizar numeración de líneas
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

# Botones
btnNuevoArchivo = Button(frameButtons, text='Nuevo archivo', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'), command=nuevo_archivo)
btnNuevoArchivo.pack(side=LEFT, padx=10, pady=10)

btnSeleccionarDirectorio = Button(frameButtons, text='Seleccionar directorio', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'), command=seleccionar_directorio)
btnSeleccionarDirectorio.pack(side=LEFT, padx=10, pady=10)

btnGuardarArchivo = Button(frameButtons, text='Guardar archivo', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'))
btnGuardarArchivo.pack(side=LEFT, padx=10, pady=10)

btnCompilar = Button(frameButtons, text='Compilar', bg=button_bg_color, fg=button_fg_color, font=('Arial', 10, 'bold'))
btnCompilar.pack(side=LEFT, padx=10, pady=10)

# Frame principal dividido en navegador y editor
frameMain = PanedWindow(root, bg=bg_color, sashwidth=5)
frameMain.pack(fill=BOTH, expand=True)

# Frame del navegador de directorios
frameDirectorio = Frame(frameMain, bg=bg_color)
frameMain.add(frameDirectorio, width=250)

labelDirectorio = Label(frameDirectorio, text="Navegador de directorios", bg=bg_color, fg=fg_color, font=('Arial', 10, 'bold'))
labelDirectorio.pack(fill=X)

lista_directorio = Listbox(frameDirectorio, bg='#252526', fg=fg_color, selectbackground=button_bg_color, selectforeground=button_fg_color)
lista_directorio.pack(fill=BOTH, expand=True, padx=5, pady=5)

lista_directorio.insert(END, "Directorio no seleccionado")
lista_directorio.bind('<Double-Button-1>', manejar_click_directorio)

# Notebook para las pestañas
notebook = ttk.Notebook(frameMain)
frameMain.add(notebook)

# Crear la primera pestaña
pestaña_inicial = Frame(notebook, bg=bg_color)
notebook.add(pestaña_inicial, text="Archivo 1")
configurar_editor(pestaña_inicial)

# Consola de salida
frameConsole = Frame(root, bg=bg_color)
frameConsole.pack(side=BOTTOM, fill=X)

consola = Text(frameConsole, bg='#252526', fg=fg_color, height=10, wrap='word', state='disabled')
consola.pack(fill=X, padx=10, pady=10)

root.mainloop()
