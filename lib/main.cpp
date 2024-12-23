#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <stdio.h>
#include <string.h>
#include <string>
#include <thread>
#include <algorithm>
#include <cstdlib>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <SDL.h>
#include <SDL_ttf.h>
#define FPS 60
class DisplayData
{
    static DisplayData *instance;

public:
    DisplayData() {}
    static DisplayData *getInstance()
    {
        if (instance == nullptr)
        {
            instance = new DisplayData();
        }
        return instance;
    }
    int width, height;
};
DisplayData *DisplayData::instance = nullptr;
class Circle
{
    std::vector<SDL_Color> colors;
    int x, y, radius, index;
    int tx, ty; // tradjectory x and y
    int window_x, window_y;

    int random_number(int min, int max)
    {
        std::random_device rd;  // obtain a random number from hardware
        std::mt19937 gen(rd()); // seed the generator
        std::uniform_int_distribution<> distr(min, max);
        return distr(gen);
    }

public:
    Circle()
    {
        radius = random_number(20, 70);
        window_x = DisplayData::getInstance()->width;
        window_y = DisplayData::getInstance()->height;
        int xmax = window_x - radius - 1;
        int ymax = window_y - radius - 1;
        x = random_number(radius + 1, xmax);
        y = random_number(radius + 1, ymax);
        int txmin, txmax, tymin, tymax;

        if (x == xmax / 2)
        {
            txmin = -3;
            txmax = 3;
        }
        else if (x < xmax / 2)
        {
            txmin = -3;
            txmax = 1;
        }
        else if (x > xmax / 2)
        {
            txmin = 1;
            txmax = 3;
        }

        tymin = 1;
        tymax = 3;
        tx = random_number(txmin, txmax);
        ty = random_number(tymin, tymax);
        {
            SDL_Color color = {120, 130, 164, 255};
            colors.push_back(color);
        }
        {
            SDL_Color color = {189, 189, 189, 255};
            colors.push_back(color);
        }
        {
            SDL_Color color = {239, 239, 239, 255};
            colors.push_back(color);
        }
        index = random_number(0, 2);
    }

public:
    void draw(SDL_Renderer *renderer)
    {

        SDL_SetRenderDrawColor(renderer, colors[index].r, colors[index].g, colors[index].b, colors[index].a); // set circle draw color
        for (int w = 0; w < radius * 2; w++)
        {
            for (int h = 0; h < radius * 2; h++)
            {
                int dx = radius - w; // horizontal offset
                int dy = radius - h; // vertical offset
                if ((dx * dx + dy * dy) <= (radius * radius))
                {
                    SDL_RenderDrawPoint(renderer, x + dx, y + dy);
                }
            }
        }
    }
    void update()
    {
        x += tx;
        y += ty;
        if (x - radius <= 0 || x + radius >= window_x)
        {
            tx *= -1;
        }
        if (y - radius <= 0 || y + radius >= window_y)
        {
            ty *= -1;
        }
    }
};

enum MODE
{
    TIME,
    WEATHER,
    CALENDER
};
class Resource
{
    static Resource *instance;
    std::string resourcePath;
    bool pathExists(std::string path)
    {
        struct stat buffer;
        return (stat(path.c_str(), &buffer) == 0);
    }

public:
    Resource()
    {
        std::string local = "";
#ifdef __APPLE__
        local = "local/";
#endif
        resourcePath = "/usr/" + local + "share/smartscreen/";
        if (!pathExists(resourcePath))
        {
            resourcePath = "./";
        }
    }
    static Resource *getInstance()
    {
        if (instance == nullptr)
        {
            instance = new Resource();
        }
        return instance;
    }
    std::string getPath()
    {
        return resourcePath;
    }
    void createFile(std::string relativePath)
    {
        std::string path = resourcePath + relativePath;
        std::ofstream(path.c_str());
    }
    int deleteFile(std::string relativePath)
    {
        std::string path = resourcePath + relativePath;
        return remove(path.c_str());
    }
};
Resource *Resource::instance = nullptr;

class Font
{
    SDL_Renderer *renderer;
    TTF_Font *font;
    SDL_Texture *upper_text_texture, *lower_text_texture;
    SDL_Color color;
    std::string text, old_text;
    int x, y;
    int upper_texW, lower_texW;
    int upper_texH, lower_texH;
    int window_width, window_height;
    MODE current_mode;

private:
    void remove_whitespace(std::string &str)
    {
        str.erase(remove(str.begin(), str.end(), ' '), str.end());
    }

public:
    Font(SDL_Renderer *renderer, int x, int y, int font_size) : renderer(renderer), x(x), y(y)
    {
        std::string path = Resource::getInstance()->getPath() + "assets/lato/Lato-Light.ttf";
        std::cout << path << std::endl;

        font = TTF_OpenFont(path.c_str(), font_size);
        if (font == nullptr)
        {
            std::cout << "ERROR: unable to open assets folder." << std::endl;
        }
        color.r = 255;
        color.g = 255;
        color.b = 255;
        color.a = 255;
        SDL_GetRendererOutputSize(renderer, &window_width, &window_height);
    }
    ~Font()
    {
        TTF_CloseFont(font);
        SDL_DestroyTexture(upper_text_texture);
        SDL_DestroyTexture(lower_text_texture);
    }

public:
    void change_text(std::string new_text)
    {
        text = new_text;

        if (text.find("\n") != std::string::npos)
        {
            current_mode = CALENDER;
            std::cout << "calender" << std::endl;
        }
        else if (text.find(":") != std::string::npos)
        {
            current_mode = TIME;
            std::cout << "time" << std::endl;
        }
        else
        {
            current_mode = WEATHER;
            std::cout << "weather" << std::endl;
        }
    }
    void display()
    {
        std::string beg = "";
        std::string end = "";
        bool found = false;
        if (old_text != text)
        {
            old_text = text;
            if (!found)
            {
                SDL_Surface *surface = TTF_RenderText_Solid(font,
                                                            text.c_str(), color);

                upper_text_texture = SDL_CreateTextureFromSurface(renderer, surface);
                lower_text_texture = nullptr;
                SDL_FreeSurface(surface);
            }
            if (found || text.find('\n') != std::string::npos)
            {
                end = text.substr(0, text.find('\n'));
                beg = text.substr(text.find('\n'), text.length() - 1);
                // remove_whitespace(end);
                found = true;
            }
            if (found)
            {
                beg.erase(beg.find('\n'), beg.find('\n') + 1);
                SDL_Surface *top = TTF_RenderText_Solid(font,
                                                        beg.c_str(), color);

                SDL_Surface *bot = TTF_RenderText_Solid(font,
                                                        end.c_str(), color);
                upper_text_texture = SDL_CreateTextureFromSurface(renderer, top);
                lower_text_texture = SDL_CreateTextureFromSurface(renderer, bot);
                SDL_FreeSurface(top);
                SDL_FreeSurface(bot);
            }
        }
        SDL_QueryTexture(upper_text_texture, NULL, NULL, &upper_texW, &upper_texH);
        SDL_QueryTexture(lower_text_texture, NULL, NULL, &lower_texW, &lower_texH);
        if (current_mode == CALENDER)
        {
            lower_texH /= 2;
            lower_texW /= 2;
        }
        if (text.find('\n') != std::string::npos)
        {
            SDL_Rect dst_up = {x - upper_texW / 2, y - upper_texH / 2 - upper_texH / 3, upper_texW, upper_texH};

            SDL_Rect dst_low = {x - lower_texW / 2, y - lower_texH / 2 + lower_texH / 3, lower_texW, lower_texH};

            SDL_RenderCopy(renderer, upper_text_texture, NULL, &dst_up);
            SDL_RenderCopy(renderer, lower_text_texture, NULL, &dst_low);

            return;
        }
        SDL_Rect dst = {x - upper_texW / 2, y - upper_texH / 2, upper_texW, upper_texH};
        SDL_RenderCopy(renderer, upper_text_texture, NULL, &dst);
    }
};

class Fifo
{

public:
    std::string mem_read()
    {
        std::ifstream fifo;
        fifo = std::ifstream("/tmp/fifo");
        std::string lns, ln;
        if (fifo.is_open())
        {
            while (std::getline(fifo, lns))
            {
                ln += lns;
            }
            fifo.close();
        }
        if (ln.find('|') != std::string::npos)
        {
            ln.replace(ln.find('|'), 1, "/");
            ln.replace(ln.find('|'), 1, "\n");
        }
        return ln;
    };
};

int main(int argc, char *argv[])
{

    SDL_Init(SDL_INIT_EVERYTHING); // Init SDL2
    TTF_Init();
    //
    SDL_Color data_color = {200, 200, 200};
    // Get monitor size
    SDL_DisplayMode display_mode;
    SDL_GetCurrentDisplayMode(0, &display_mode);
    int monitor_width = display_mode.w;
    int monitor_height = display_mode.h;
    //
    SDL_Window *window = nullptr;     // window
    SDL_Renderer *renderer = nullptr; // renderer
    Font *font = nullptr;
    SDL_Event e;
    Fifo *fifo;

    bool done = false;
    std::string data = "";
    //

    window = SDL_CreateWindow("x",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              monitor_width, monitor_height,
                              SDL_WINDOW_FULLSCREEN); // Create window
    SDL_SetHint(SDL_HINT_RENDER_DRIVER, "software");
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_PRESENTVSYNC); // Create renderer
    SDL_GetRendererOutputSize(renderer, &monitor_width, &monitor_height);

    DisplayData::getInstance()->width = monitor_width;
    DisplayData::getInstance()->height = monitor_height;

    font = new Font(renderer, monitor_width / 2, monitor_height / 2, 200 * monitor_width / 1440);
    fifo = new Fifo();
    data = fifo->mem_read();
    font->change_text(data);

    // cricle array
    int x = (double(monitor_height * monitor_width) / 2) / double((1920 * 1080) / 2) * 10;
    Circle circles[x];
    // Update tick
    int updateTick = 0; // update info every 10 ticks
    pid_t python_pid = -1;
    auto run_script = [&python_pid](const char *file)
    {
        std::string path = Resource::getInstance()->getPath() + file;
        std::cout << path << std::endl;
        pid_t fk = fork();
        if (!fk)
        {
            if (execl(path.c_str(), NULL) == -1)
            {
                perror("Failed to exec!\n");
            }
            python_pid = fk;
        }
        else if (fk == -1)
        {
            perror("fork");
        }
        int status;
        wait(&status);
        printf("child pid was %d, it exited with %d\n", fk, status);
    };
    std::thread python(run_script, "build/smartscreen-python");
    // Application Loop
    while (!done)
    {
        Uint32 starttime = SDL_GetTicks();
        ++updateTick;
        if (updateTick == 10)
        {
            std::string new_data = fifo->mem_read();
            if (data != new_data)
            {
                data = new_data;
                font->change_text(data);
            }
            updateTick = 0;
        }

        SDL_RenderPresent(renderer);                       // update screen
        SDL_SetRenderDrawColor(renderer, 79, 79, 79, 255); // set draw color as background color
        SDL_RenderClear(renderer);                         // clear screen so it is a solid color
        for (int i = 0; i < sizeof(circles) / sizeof(Circle); ++i)
        {
            circles[i].update();
            circles[i].draw(renderer);
        }
        font->display();
        while (SDL_PollEvent(&e))
        {
            if (e.type == SDL_QUIT)
                done = true;
            else if (e.type == SDL_KEYDOWN)
            {
                switch (e.key.keysym.sym)
                {
                case SDLK_ESCAPE:
                    done = true;
                    break;
                }
            }
        }

        Uint32 endtime = SDL_GetTicks();
        Uint32 deltatime = endtime - starttime;
        if (deltatime < (1000 / FPS))
        {
            usleep((1000000 / FPS) - deltatime);
        }
    }

    // destroy
    fifo->~Fifo();
    //
    SDL_DestroyWindow(window);
    SDL_DestroyRenderer(renderer);
    //
    SDL_Quit();
    TTF_Quit();
    //

    Resource::getInstance()->createFile("end");
    python.join();
    Resource::getInstance()->deleteFile("end");
    return 0;
}