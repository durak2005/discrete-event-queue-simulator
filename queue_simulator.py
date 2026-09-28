import numpy as np
import heapq
import matplotlib.pyplot as plt

def simulate_m_m_s_queue(arrival_rate, service_rate, num_servers, sim_duration):
    """
    Öncelikli kuyruk (heap) tabanlı kesikli olay simülasyonu.
    Gelişler: Poisson (Üstel aralıklarla), Servis: Üstel dağılım.
    """
    np.random.seed(42)
    current_time = 0.0
    queue = []
    server_busy_until = [0.0] * num_servers
    
    time_points = [0.0]
    queue_lengths = [0]
    waiting_times = []
    
    # İlk geliş olayı
    events = [(np.random.exponential(1.0 / arrival_rate), 'ARRIVAL')]
    heapq.heapify(events)
    
    while events:
        current_time, event_type = heapq.heappop(events)
        if current_time > sim_duration:
            break
            
        if event_type == 'ARRIVAL':
            # Yeni bir sonraki geliş olayını kuyruğa planla
            next_arrival = current_time + np.random.exponential(1.0 / arrival_rate)
            if next_arrival <= sim_duration:
                heapq.heappush(events, (next_arrival, 'ARRIVAL'))
                
            # Boşta sunucu var mı kontrol et
            available_servers = [i for i, busy_t in enumerate(server_busy_until) if busy_t <= current_time]
            
            if available_servers:
                server_idx = available_servers[0]
                serv_time = np.random.exponential(1.0 / service_rate)
                server_busy_until[server_idx] = current_time + serv_time
                heapq.heappush(events, (server_busy_until[server_idx], f'DEPARTURE_{server_idx}'))
                waiting_times.append(0.0)
            else:
                queue.append(current_time)
                
            time_points.append(current_time)
            queue_lengths.append(len(queue))
            
        elif 'DEPARTURE' in event_type:
            server_idx = int(event_type.split('_')[1])
            if queue:
                arrival_t = queue.pop(0)
                waiting_times.append(current_time - arrival_t)
                serv_time = np.random.exponential(1.0 / service_rate)
                server_busy_until[server_idx] = current_time + serv_time
                heapq.heappush(events, (server_busy_until[server_idx], f'DEPARTURE_{server_idx}'))
            else:
                server_busy_until[server_idx] = 0.0
                
            time_points.append(current_time)
            queue_lengths.append(len(queue))
            
    return time_points, queue_lengths, waiting_times

def plot_queue_results(times, lengths, waits):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 1. Kuyruk Boyu Zaman Serisi (Step grafiği)
    ax1.step(times, lengths, where='post', color='#2563eb', linewidth=1.5)
    ax1.fill_between(times, lengths, step='post', color='#93c5fd', alpha=0.3)
    ax1.set_title("Zamana Göre Kuyruk Boyu Dinamiği (M/M/3 Modeli)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Kuyruktaki İş/Müşteri Sayısı")
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    # 2. Bekleme Süresi Histogramı
    ax2.hist(waits, bins=30, color='#10b981', edgecolor='black', alpha=0.85, density=True)
    avg_wait = np.mean(waits)
    ax2.axvline(avg_wait, color='#dc2626', linestyle='--', linewidth=2, label=f'Ortalama Bekleme: {avg_wait:.2f} dk')
    ax2.set_title("Kuyrukta Bekleme Süresi Olasılık Dağılımı", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Bekleme Süresi (Dakika)")
    ax2.set_ylabel("Olasılık Yoğunluğu")
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig("queue_simulation_results.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    lambda_param = 1.8   # Dakikada ortalama 1.8 müşteri gelişi
    mu_param = 0.7       # Sunucu başına dakikada 0.7 servis tamamlama
    servers = 3          # 3 paralel sunucu/banko
    duration = 480       # 8 saatlik (480 dk) vardiya
    
    t_pts, q_lens, w_times = simulate_m_m_s_queue(lambda_param, mu_param, servers, duration)
    print(f"Simülasyon Tamamlandı! Ortalama Bekleme Süresi: {np.mean(w_times):.2f} dk")
    print(f"Maksimum Kuyruk Uzunluğu: {max(q_lens)} kişi")
    plot_queue_results(t_pts, q_lens, w_times)
